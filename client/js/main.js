var computeMainWindowHeight = function() {
	return $(document.body).outerHeight(true) - $('header').outerHeight(true);
};

var computeCodeEditorWidth = function () {
	return $('#main_div').outerWidth(true) - $('#partition_tree_div').outerWidth(true) - 1;
}

var resizeDivs = function() {
	$('#main_div').width($(document.body).outerWidth(true));
	$('#main_div').height(computeMainWindowHeight());
	$('#code_editor_div').width(computeCodeEditorWidth());
	$('#code_editor_div').height(computeMainWindowHeight());
}

var onResize = function() {
	resizeDivs();
	// Mergely should update the height of CodeMirror lib but it doesn't
	$('.CodeMirror').css({'height' : computeMainWindowHeight(), 
		'width' : (computeCodeEditorWidth() / 2 - 50) + 'px'});
	$('#code_editor').mergely('resize');
};

var initPartitionTree = function () {
	$('#partition_tree').jstree({
		'core' : {
			'data' : ['No pull request selected.']
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
		
		if (text.endsWith("]")) {
			$('#code_editor').mergely('scrollTo', 'rhs', selected.node.original.line_start);
		}
	});
};

var initCodeEditor = function() {
	$('#code_editor').mergely({
		cmsettings: { readOnly: true, lineNumbers: true },
		editor_height: 'auto', //~ computeMainWindowHeight() + 'px',
		editor_width: 'auto',
		height: function(h) {
			return computeMainWindowHeight();
		},
		width: function(w) {
			//~ $('#code_editor').css({'display': 'inline-block', 'float': 'left', 'clear': 'none'});
			return computeCodeEditorWidth();
		}
	});
};

var parseURL = function(url) {
	var parser = document.createElement('a');
	parser.href = url;
	return parser;
	//~ Given "http://example.com:3000/pathname/?search=test#hash"
	//~ parser.protocol; // => "http:"
	//~ parser.hostname; // => "example.com"
	//~ parser.port;     // => "3000"
	//~ parser.pathname; // => "/pathname/"
	//~ parser.search;   // => "?search=test"
	//~ parser.hash;     // => "#hash"
	//~ parser.host;     // => "example.com:3000"
}

$(document).ready(function() {
	resizeDivs();
	initPartitionTree();
	initCodeEditor();
	
	$('#pull_request_url_input').keyup(function(event) {
		if(event.keyCode == 13) { // Enter/Return key
			$("#partition_button").click();
		}
	});
	
	$('#partition_button').click(function () {
		var url = $('#pull_request_url_input').val();
		var parsedURL = parseURL(url);
		// '', projectOwner, projectName, 'pull', pullRequestId
		var paths = parsedURL.pathname.split('/'); 
		var projectOwner = paths[1];
		var projectName = paths[2];
		var pullRequestId = parseInt(paths[4], 10);
		
		if (paths[0] !== '' || paths[3] !== 'pull' || paths[4] === NaN) {
			alert('Error: Invalid URL. The provided URL must follow the format: https://github.com/ORGANIZATION/PROJECT/pull/X');
			return;
		}
		
		var partitionsUrl = './pulls/' + projectOwner + '/' + projectName + '/' + pullRequestId + '/partitions/';
		
		$('#partition_tree').jstree(true).settings.core.data = {
					"url" : partitionsUrl,
					"dataType" : "json"
		};
		$('#partition_tree').jstree(true).refresh();
	});
	
	$('#menu_button').click(function () {
		if ($('#about_div').is(":hidden")) {
			$('#about_div').slideDown("slow");
		} else {
			$('#about_div').slideUp("fast");
		}
	});
	
	$('#about_close_button').click(function () {
		$('#about_div').slideUp("fast");
	});
	
	$(window).trigger('resize');
});

$(window).resize(onResize);
