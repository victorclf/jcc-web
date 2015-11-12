$(document).ready(function() {
	$('#partition_tree').jstree({
		'core' : {
			'data' : {
				"url" : "./test/examples/toy_example/partitions.json",
				"dataType" : "json"
			}
		}
	});
	
	$('#partition_tree').on("loaded.jstree", function () {
		$('#partition_tree').jstree().open_all();
	});
	
	
	$('#code_editor').mergely({
		cmsettings: { readOnly: false, lineNumbers: true },
		lhs: function(setValue) {
			setValue('the quick red fox\njumped over the hairy dog');
		},
		rhs: function(setValue) {
			setValue('the quick brown fox\njumped over the lazy dog');
		}
	});
});
