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
	
	$('#partition_tree').on("select_node.jstree", function (node, selected, event) {
		var text = selected.node.text;
		if (text.endsWith(".java")) {
			$.get(selected.node.original.before_file, function (data) {
				$('#code_editor').mergely('lhs', data);
			}, "text");
			
			$.get(selected.node.original.after_file, function (data) {
				$('#code_editor').mergely('rhs', data);
			}, "text");
		}
		
		//~ if (text.endsWith("]")) {
			//~ $('#code_editor').mergely('scrollTo', 'rhs', selected.node.original.line_start);
		//~ }
	});
	
	
	$('#code_editor').mergely({
		cmsettings: { readOnly: false, lineNumbers: true },
		lhs: function(setValue) {
			setValue('No diff-region selected.');
		},
		rhs: function(setValue) {
			setValue('No diff-region selected.');
		}
	});
});
