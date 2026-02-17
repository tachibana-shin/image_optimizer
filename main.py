import os, zipfile, tempfile
from datetime import datetime, timezone
from qt.core import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox
from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog, info_dialog
from calibre.gui2 import Dispatcher
from calibre.utils.config import JSONConfig
from calibre_plugins.image_optimizer import get_resources

from calibre.ebooks.metadata.meta import set_metadata

from . import ImageOptimizerPlugin
from .optimizer import optimize_image_logic
from .config_dialog import ConfigDialog

# prefsは現在config_dialog.pyで管理されていますが、ここで必要になるかもしれません。
# 実際にはConfigDialogがそれを管理し、パラメータをジョブに渡します。
# ただし、元のmain.pyの15〜21行目ではデフォルトを設定しています。デフォルトの設定を維持するか、移動する必要があります。
# ここに置くか、config_dialogに置くのが良いでしょう。config_dialogはcalibre.utils.configからインポートするため、
# デフォルトの処理はconfig_dialogの初期化に任せるか、ここで行うことができます。
# プラグインのロード時に確実に設定されるように、ここでデフォルトの初期化を維持しましょう。

from .config_dialog import prefs
prefs.defaults.update({
    'size': '1080',
    'quality': '85',
    'format': 'Original',
    'keep_time_import': True
})

def get_image_type(data):
    if not data or len(data) < 12:
        return None

    # 最も一般的なフォーマット
    if data.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'webp'
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return 'gif'
    
    # グラフィックおよび技術的なフォーマット
    if data.startswith(b'BM'):
        return 'bmp'
    if data.startswith(b'II\x2a\x00') or data.startswith(b'MM\x00\x2a'):
        return 'tiff'
    if data[:4] in (b'\x00\x00\x01\x00', b'\x00\x00\x02\x00'):
        return 'ico' # .curを含む
    
    # モダンおよびHDRフォーマット
    if data[4:12] in (b'ftypavif', b'ftypavis'):
        return 'avif'
    if data.startswith(b'qoif'):
        return 'qoi'
    if data.startswith(b'#?RADIANCE') or data.startswith(b'\x0a\x20\x20\x20'):
        return 'hdr'
    if data.startswith(b'\x76\x2f\x31\x01'):
        return 'openexr'
    
    # ゲームフォーマットその他
    if data.startswith(b'DDS '):
        return 'dds'
    if data.startswith(b'farbfeld'):
        return 'farbfeld'
    if data[:3] in (b'P1\n', b'P2\n', b'P3\n', b'P4\n', b'P5\n', b'P6\n'):
        return 'pnm' # PBM、PGM、PPMを含む
    
    # TGAは先頭にマジックバイトがありません（通常は末尾にあります）、
    # しかしimageクレートはそれをサポートしているため、必要に応じて 'tga' にフォールバックできます
    
    return None

def do_single_optimization(book_id, params, db_path, book_mi, formats_data, abort=None, log=None, notifications=None):
    optimized_formats = {}
    stats = {}
    
    # 大規模な進行状況を分割するために合計フォーマットを計算
    total_fmts = len(formats_data)
    
    for fmt_idx, (fmt, path) in enumerate(formats_data.items()):
        if abort and abort.is_set(): break
        if not path or not os.path.exists(path): continue
        
        if zipfile.is_zipfile(path):
            old_size = os.path.getsize(path)
            fd, temp_out = tempfile.mkstemp(suffix=f'.{fmt.lower()}')
            os.close(fd)

            try:
                with zipfile.ZipFile(path, 'r') as yin, \
                     zipfile.ZipFile(temp_out, 'w') as yout:
                    
                    all_files = yin.namelist()
                    total_items = len(all_files)
                    
                    for item_idx, item in enumerate(yin.infolist()):
                        # 解凍の途中でユーザーがキャンセルを押したかどうかを確認
                        if abort and abort.is_set(): break
                        
                        if item.filename == 'mimetype': continue
                        
                        data = yin.read(item.filename)
                        
                        # 詳細な進行状況を更新（比率 0.0 -> 1.0）
                        # 式: (前のフォーマットの進行状況) + (このフォーマットの現在のアイテムの進行状況)
                        if notifications:
                            item_progress = item_idx / total_items
                            # 各ブックフォーマットに重みを均等に分配
                            overall_progress = (fmt_idx + item_progress) / total_fmts
                            notifications.put((overall_progress, f"Processing {fmt}: {item.filename}"))

                        if get_image_type(data):
                            data = optimize_image_logic(data, params)
                            yout.writestr(item, data)
                        else:
                            # fuck compress deflate detect type
                            compress = zipfile.ZIP_STORED if item.filename == 'mimetype' else zipfile.ZIP_DEFLATED
                            yout.writestr(item, data, compress_type=compress)

                # 圧縮後にメタデータを埋め込む
                try:
                    if notifications:
                        notifications.put(((fmt_idx + 0.9) / total_fmts, f"Embedding metadata into {fmt}..."))
                    with open(temp_out, 'r+b') as f:
                        set_metadata(f, book_mi, fmt.lower())
                except Exception as emeta:
                    if log: log.warning(f"Could not embed metadata into {fmt}: {str(emeta)}")
                
                new_size = os.path.getsize(temp_out)
                optimized_formats[fmt] = temp_out

                if log:
                    reduction = ((old_size - new_size) / old_size) * 100 if old_size > 0 else 0
                    log(f"[{fmt}] {old_size/1024:.1f}KB -> {new_size/1024:.1f}KB (Reduced {reduction:.1f}%)")
            
                stats[fmt] = (old_size, new_size)
            except Exception as e:
                if log: log.error(f"Error {fmt}: {str(e)}")
                if os.path.exists(temp_out): os.remove(temp_out)

    # 最後に100% (1.0) を返すことを確認
    if notifications:
        notifications.put((1.0, "File processing completed."))
        
    return book_mi, optimized_formats, stats, params.get('keep_time_import', True)

class ImageOptimizerAction(InterfaceAction):
    action_spec = ('Image Optimizer', get_icons('images/icon.png'), 'Batch Optimize Images', None)
    name = ImageOptimizerPlugin.name

    def genesis(self):
        self.qaction.triggered.connect(self.ask_user)
        self.summary_report = []

    def ask_user(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows: return error_dialog(self.gui, "Error", "Please select at least one book!", show=True)
        params = self.get_params_from_dialog()
        if not params: return
        ids = [self.gui.library_view.model().id(r) for r in rows]
        self.new_book_ids = []
        self.total_to_process = len(ids)
        self.summary_report = []
        self.processed_count = 0
        from calibre.gui2.threaded_jobs import ThreadedJob
        for book_id in ids:
            db = self.gui.current_db
            mi = db.get_metadata(book_id, index_is_id=True, get_cover=True)
            mi.title = f"{mi.title} [optimized]" # Metadataオブジェクトのタイトルを変更
            fmts = [f.strip().upper() for f in (db.formats(book_id, index_is_id=True) or '').split(',') if f.strip()]
            formats_data = {f: db.format_path(book_id, f, index_is_id=True) for f in fmts}
            job = ThreadedJob(
                type_='image_optimizer_single',
                description=f"Optimizing: {mi.title}",
                func=do_single_optimization,
                args=(book_id, params, db.library_path, mi, formats_data),
                kwargs={},
                callback=Dispatcher(self.on_single_job_finished)
            )
            self.gui.job_manager.run_threaded_job(job)

    def on_single_job_finished(self, job):
        self.processed_count += 1
        if not job.failed and job.result:
            mi, optimized_formats, stats, keep_time_import = job.result
            if optimized_formats:
                db = self.gui.current_db

                if not keep_time_import:
                    mi.timestamp = datetime.now(timezone.utc)

                new_id = db.create_book_entry(mi, add_duplicates=True)

                total_old = 0
                total_new = 0
                
                for fmt, temp_path in optimized_formats.items():
                    # add_format_with_path は新しい mi.title を使用してファイル .epub/.pdf に名前を付けます
                    db.new_api.add_format(new_id, fmt, temp_path, run_hooks=False)
                    self.gui.library_view.model().refresh_ids([new_id])
                    
                    old_sz, new_sz = stats.get(fmt, (0, 0))
                    total_old += old_sz
                    total_new += new_sz

                # self.gui.library_view.model().books_added(1)
                if os.path.exists(temp_path):
                    try: os.remove(temp_path)
                    except: pass
                self.new_book_ids.append(new_id)
                reduction = ((total_old - total_new) / total_old) * 100
                self.summary_report.append(f"• {mi.title}: Reduced {reduction:.1f}%")

        if self.processed_count >= self.total_to_process:
            self.gui.library_view.model().refresh_ids(self.new_book_ids)
            # if self.new_book_ids: self.gui.library_view.select_rows(self.new_book_ids)
            # info_dialog(self.gui, "Completed", f"Optimized {len(self.new_book_ids)} books.", show=True)
            self.show_final_report()

    def show_final_report(self):
        # self.gui.library_view.model().refresh_ids(self.new_book_ids)
        
        report_text = "\n".join(self.summary_report)
        msg = f"Optimized {len(self.new_book_ids)} books.\n\nChange details:\n{report_text}"
        
        # 結果ダイアログを表示
        info_dialog(self.gui, "Optimization Report", msg, show=True)

    def get_params_from_dialog(self):
        d = ConfigDialog(self.gui)
        if d.exec() == QDialog.Accepted: return d.get_values()
        return None