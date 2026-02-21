from calibre.customize import InterfaceActionBase
from calibre.utils.localization import _

load_translations()  # type: ignore

class ImageOptimizerPlugin(InterfaceActionBase):
    name                = _('Image Optimizer')
    description         = _('Batch compress and optimize images')
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Tachibana Shin'
    version             = (1, 0, 1)
    actual_plugin       = 'calibre_plugins.image_optimizer.main:ImageOptimizerAction'
