{
	'name': 'Document Management',
	'description': 'Manage your personal Document tasks.',
	'author': 'Duy Nguyen',
	'depends': ['base','mail','hr','mail_template_demo'],
	'application': True,
	# 'images':['images/icon.png'],
	'data': [
		'views/qlcv_menu.xml',
        'views/qlcv_view.xml',
		'security/qlcv_access_rule.xml'
	],
	'demo' : [
		'data/doc_task.csv'
		# 'data/doc_data.xml'
	],
}
