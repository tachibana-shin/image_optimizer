import io
from PIL import Image

from calibre.utils.localization import _

load_translations()  # type: ignore

def optimize_image_logic(img_data, params):
    try:
        image = Image.open(io.BytesIO(img_data))
        orig_format = image.format
        w, h = map(float, image.size)

        quality = int(params.get('quality', 100)) if params.get('quality') != '' else 100
        encoding_type = params.get('format', _("Original"))
        
        target_format = encoding_type if encoding_type != _("Original") else orig_format
        if not target_format: target_format = 'JPEG' # 安全なフォールバック

        if params.get('size') != '':
            max_px_size = float(params.get('size'))
            if w < h:
              if w > max_px_size:
                new_w = max_px_size
                new_h = h * (max_px_size / w)
                image = image.resize((int(new_w), int(new_h)), Image.Resampling.LANCZOS)
            else:
              if h > max_px_size:
                new_h = max_px_size
                new_w = w * (max_px_size / h)
                image = image.resize((int(new_w), int(new_h)), Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        save_args = {'optimize': True}
        fmt_upper = target_format.upper()

        # 特定のカラーモードを処理
        # JPEG/BMP/EPS はアルファチャンネル（透明度）をサポートしていません
        if fmt_upper in ('JPEG', 'JPG', 'BMP', 'EPS'):
            if image.mode in ("RGBA", "P", "LA"):
                image = image.convert('RGB')
        
        # フォーマットごとの圧縮パラメータを設定
        if fmt_upper in ('JPEG', 'JPG'):
            save_args.update({'quality': quality, 'progressive': True, 'subsampling': '4:2:0', 'keep_rgb': False})
        elif fmt_upper == 'WEBP':
            save_args.update({'quality': quality, 'method': 6})
        elif fmt_upper == 'PNG':
            save_args.update({'compress_level': 9}) # PNGは品質の代わりに圧縮レベルを使用
        elif fmt_upper == 'TIFF':
            save_args.update({'compression': 'tiff_lzw'})
        elif fmt_upper == 'GIF':
            # アニメーションGIFの場合は image.save(..., save_all=True) を使用する必要がありますが、ここでは単一フレームのみを最適化しますか？
            # 元のコードには 'interlace': True のみが含まれていました。
            save_args.update({'interlace': True})
        else:
            # QOI, TGA, BMP などの他のフォーマットは品質を使用しません
            pass

        # "unexpected keyword argument" エラーを避けるために柔軟なパラメータを使用
        try:
            image.save(buf, format=target_format, **save_args)
        except (ValueError, TypeError):
            # 'optimize' をサポートしていない奇妙なフォーマットの場合は、純粋に保存を試みる
            image.save(buf, format=target_format)

        return buf.getvalue()

    except Exception as e:
        print(f"Optimization error: {str(e)}") # エラーメッセージは翻訳済み
        return img_data # エラーが発生した場合は本を破損しないように元のデータを返す
