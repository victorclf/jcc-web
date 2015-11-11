$(document).ready(function() {
	$('#jstree_partition_div').jstree({
		'core' : {
			'data' : {
				"url" : "./test/examples/toy_example/partitions.json",
				"dataType" : "json"
			}
		}
	});
});
