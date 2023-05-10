
{
    'name': 'Real Estate',
    'author': 'Akshaya',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/properties_views.xml',
        'views/properties_types_views.xml',
        'views/properties_tags_views.xml',
        'views/propertiesmoveline_views.xml',

    ],
   'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
