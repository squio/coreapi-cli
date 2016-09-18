import pkg_resources
import collections


def sorting_func(package_info):
    """
    A sorting order for (package, codec_class) tuples. Example ordering:

    application/coreapi+json  (highest priority)
    application/openapi+json  (lower as not a coreapi package built-in)
    application/json          (lower as more general subtype)
    text/*                    (lower as sub type is wildcard)
    */*                       (lowest as main type is wildcard)
    """
    package, codec_class = package_info
    media_type = getattr(codec_class, 'media_type')
    main_type, _, sub_type = media_type.partition('/')
    sub_type = sub_type.split(';')[0]
    is_builtin = package.dist.project_name == 'coreapi'
    return (
        main_type == '*',
        sub_type == '*',
        '+' not in sub_type,
        not is_builtin,
        media_type
    )


def get_codec_packages():
    """
    Returns a list of (package, codec_class) tuples.
    """
    packages = [
        (package, package.load()) for package in
        pkg_resources.iter_entry_points(group='coreapi.codecs')
    ]
    packages = [
        (package, cls) for (package, cls) in packages
        if hasattr(cls, 'decode') or hasattr(cls, 'encode')
    ]
    return sorted(packages, key=sorting_func)


codec_packages = get_codec_packages()

all_codecs = collections.OrderedDict([
    (package.name, cls) for (package, cls) in codec_packages
])

decoders = collections.OrderedDict([
    (package.name, cls) for (package, cls) in codec_packages
    if hasattr(cls, 'decode')
])

encoders = collections.OrderedDict([
    (package.name, cls) for (package, cls) in codec_packages
    if hasattr(cls, 'encode')
])
