from calibre.customize import InterfaceActionBase, EditBookToolPlugin

class ImageOptimizerPlugin(InterfaceActionBase):
    name                = 'Image Optimizer'
    description         = 'Batch compress and optimize images'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Tachibana Shin'
    version             = (1, 0, 0)
    actual_plugin       = 'calibre_plugins.image_optimizer.main:ImageOptimizerAction'
