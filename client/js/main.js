// Singletons
var pathBar = function() {
	var _SEPARATOR = 'files/';
	var _realPath = '';
	var _partitionName = '';
		
	return {
		getRealPath: function() {
			return _realPath;
		},
		getUserPath: function() {
			return $('#filepath_bar').val();
		},
		getPartitionName: function() {
			return _partitionName;
		},
		setPath: function(realPath, partitionName) {
			_realPath = realPath;
			_partitionName = partitionName;
			var separatorIndex = _realPath.search(_SEPARATOR);
			var userPath = separatorIndex !== - 1
				? _realPath.slice(separatorIndex + _SEPARATOR.length)
				: _realPath;
			if (userPath) {
				userPath += ' (' + _partitionName + ')';
			}
			$('#filepath_bar').val(userPath);
		}
	}
}();

var diffRegionHighlighter = function() {
	var _diffRegions = '';
	var _selectedDiffRegion = '';
	
	return {
		clear: function() {
			_diffRegions = null;
			_selectedDiffRegion = null;
		},
		setDiffRegions: function(diffRegions) {
			// Assumes that whole document is reloaded when diff-regions 
			// to highlight are changed.
			_diffRegions = diffRegions;
			_selectedDiffRegion = null;
		},
		setSelectedDiffRegion: function(selectedDiffRegion) {
			// Assumes that the whole document is not reloaded when
			// selected diff-region change.
			var rhsCm = $('#code_editor').mergely('cm', 'rhs');
			if (_selectedDiffRegion) {
				for (var j = _selectedDiffRegion[0]; j <= _selectedDiffRegion[1]; ++j) {
					var lineId = j - 1;
					rhsCm.removeLineClass(lineId, 'background', 'diffSelected');
				}
			}
			
			_selectedDiffRegion = selectedDiffRegion;
			
			if (_selectedDiffRegion) {
				for (var j = _selectedDiffRegion[0]; j <= _selectedDiffRegion[1]; ++j) {
					var lineId = j - 1;
					rhsCm.addLineClass(lineId, 'background', 'diffSelected');
				}
			}
		},
		highlight: function() {
			var rhsCm = $('#code_editor').mergely('cm', 'rhs');
			
			if (_diffRegions) {
				var lastDiffLineId = -1;
				for (var i = 0; i < _diffRegions.length; ++i) {
					var diffRegion = _diffRegions[i];
					for (var j = diffRegion[0]; j <= diffRegion[1]; ++j) {
						var lineId = j - 1;
						rhsCm.addLineClass(lineId, 'background', 'diffFromSelectedPartition');
						// Use a thin border to separate adjacent diff-regions.
						if (lineId !== 0 && lineId === lastDiffLineId + 1) {
							rhsCm.addLineClass(lineId, 'background', 'diffFromSelectedPartitionSplit');
						}
					}
					lastDiffLineId = lineId;
				}
			}
			
			if (_selectedDiffRegion) {
				
			}
		}
	}
}();



// Functions
var displayMessageBox = function(text) {
	$('#msgbox_text').text(text);
	$('#msgbox_div').css('display', 'flex');
};

var computeMainWindowHeight = function() {
	return $(document.body).outerHeight(true) - $('header').outerHeight(true);
};

var computeCodeEditorMaxWidth = function() {
	return $('#main_div').outerWidth(true) - $('#partition_tree_div').outerWidth(true) - 1;
};

var computeCodeEditorMaxHeight = function() {
	return computeMainWindowHeight() - $('#filepath_bar').outerHeight(true);
};

var computeCodeEditorCurrentWidth = function() {
	var editorWidth = 0;
	$('#code_editor > div').each(function() {
		editorWidth += $(this).outerWidth(true);
	});
	return editorWidth;
};

var resizeDivs = function() {
	$('#main_div').width($(document.body).outerWidth(true));
	$('#main_div').height(computeMainWindowHeight());
	$('#code_editor_div').width(computeCodeEditorMaxWidth());
	$('#code_editor_div').height(computeCodeEditorMaxHeight());
	$('#faq_div_content').css('max-height', computeMainWindowHeight() + 'px');
}

var onResize = function() {
	resizeDivs();
	// Mergely should update the height of CodeMirror lib but it doesn't
	$('.CodeMirror').css({'height' : computeCodeEditorMaxHeight(), 
		'width' : (computeCodeEditorMaxWidth() / 2 - 50) + 'px'});
	$('#code_editor').mergely('resize');
	$('#filepath_bar').outerWidth(computeCodeEditorCurrentWidth() - 1);
	setTimeout(diffRegionHighlighter.highlight, 3000);
};

var clearTree = function(message) {
	$('#partition_tree').jstree(true).settings.core.data = [message ? message : 'No pull request selected.'];
	$('#partition_tree').jstree(true).refresh();
};

var clearEditor = function() {
	$('#code_editor').mergely('lhs', '');
	$('#code_editor').mergely('rhs', '');
	pathBar.setPath('', '');
	diffRegionHighlighter.clear();
};

var setEditorContent = function(lhsFileURL, rhsFileURL, partitionName, diffRegions, selectedDiffRegion, scrollToLine) {
	var lhsData, 
		rhsData;
	
	var scrollEditor = function() {
		if (scrollToLine) {
			$('#code_editor').mergely('cm', 'rhs')
				.scrollIntoView({line: scrollToLine, ch: 0}, 
								Math.floor($('#code_editor_div').height() / 2));
		}		
	};
	
	var onSuccess = function() {
		// Barrier synchronizing both AJAX calls.
		if (lhsData !== undefined && rhsData !== undefined) {
			$('#code_editor').mergely('clear', 'lhs');
			$('#code_editor').mergely('clear', 'rhs');
			$('#code_editor').mergely('lhs', lhsData);
			$('#code_editor').mergely('rhs', rhsData);
			pathBar.setPath(rhsFileURL, partitionName);
			diffRegionHighlighter.setDiffRegions(diffRegions);
			diffRegionHighlighter.setSelectedDiffRegion(selectedDiffRegion);
			setTimeout(diffRegionHighlighter.highlight, 200);
			setTimeout(scrollEditor, 50);
		}
	};
	
	var onError = function() {
		var errorMsg = 'ERROR: Failed to retrieve the file from the server!';
		$('#code_editor').mergely('lhs', errorMsg);
		$('#code_editor').mergely('rhs', errorMsg);
	};
	
	if (pathBar.getPartitionName() !== partitionName 
		|| pathBar.getRealPath() !== rhsFileURL) {
		$.get(lhsFileURL, function(data) {
			lhsData = data;
			onSuccess();
		}, "text")
			.fail(function() {
				onError();
			});
		
		$.get(rhsFileURL, function(data) {
			rhsData = data;
			onSuccess();
		}, "text")
			.fail(function() {
				onError();
			});
	} else {
		diffRegionHighlighter.setSelectedDiffRegion(selectedDiffRegion);
		diffRegionHighlighter.highlight();
		scrollEditor();
	}
};

var initPartitionTree = function() {
	$('#partition_tree').jstree({
		'core' : {
			'data' : ['No pull request selected.']
		}
	});
	
	$('#partition_tree').on("select_node.jstree", function(node, selected, event) {
		var node = selected.node;
		var selectedDiffRegion;
		var scrollToLine;
		
		if (node.text.endsWith("]")) {
			scrollToLine = node.original.line_start;
			selectedDiffRegion = [node.original.line_start, node.original.line_end];
			node = $('#partition_tree').jstree(true).get_node(node.parent);
		}
		
		if (node.text.endsWith(".java")) {
			var partitionName = $('#partition_tree').jstree(true).get_node(node.parent).text;
			
			var diffRegions = [];
			for (var i = 0; i < node.children.length; ++i) {
				var childIndex = node.children[i];
				var childNode = $('#partition_tree').jstree(true).get_node(childIndex);
				diffRegions.push([childNode.original.line_start, childNode.original.line_end]);
			}
			
			setEditorContent(node.original.before_file, node.original.after_file, partitionName, diffRegions, selectedDiffRegion, scrollToLine);
		}
	});
};

var initCodeEditor = function() {
	$('#code_editor').mergely({
		cmsettings: { readOnly: true, lineNumbers: true },
		editor_height: 'auto',
		editor_width: 'auto',
		height: function(h) {
			return computeCodeEditorMaxHeight();
		},
		width: function(w) {
			//~ $('#code_editor').css({'display': 'inline-block', 'float': 'left', 'clear': 'none'});
			return computeCodeEditorMaxWidth();
		},
		resized: function() {
			diffRegionHighlighter.highlight();
		}
	});
};

var gitHubURLToJCCURL = function(ghURL) {
	// https://github.com/<projectOwner>/<project>/pull/<pullRequestId>
	var parsedURL = parseURL(ghURL);
	// '', projectOwner, projectName, 'pull', pullRequestId
	var paths = parsedURL.pathname.split('/');
	projectOwner = paths[1];
	projectName = paths[2];
	pullRequestId = parseInt(paths[4], 10);
	
	if (paths[0] !== '' || paths[3] !== 'pull' || pullRequestId === NaN) {
		throw { name: 'InvalidGitHubPullRequestURLException' };
	}
	
	return '/pulls/' + projectOwner + '/' + projectName + '/' + pullRequestId + '/';
};

var jccURLToGitHubURL = function(jccURL) {
	var parsedURL = parseURL(jccURL);
	// '', 'pulls', projectOwner, projectName, pullRequestId
	var paths = parsedURL.pathname.split('/');
	projectOwner = paths[2];
	projectName = paths[3];
	pullRequestId = parseInt(paths[4], 10);
	
	if (paths[0] !== '' || paths[1] !== 'pulls' || pullRequestId === NaN) {
		throw { name: 'InvalidJCCPullRequestURLException' };
	}
	
	return 'https://github.com/' + projectOwner + '/' + projectName + '/pull/' + pullRequestId;
};

var startLoadingState = function() {
	$('#loadingbox_div').css('display', 'flex');
	//~ $('#pull_request_url_input').prop('disabled', 'true');
	//~ $('partition_button').prop('disabled', 'true');
};

var stopLoadingState = function() {
	$('#loadingbox_div').css('display', 'none');
	//~ $('#pull_request_url_input').prop('disabled', 'false');
	//~ $('#partition_button').prop('disabled', 'false');
};

var partitionPullRequest = function() {
	var url = $('#pull_request_url_input').val();
	
	var pullURL;
	try {
		pullURL = gitHubURLToJCCURL(url);
	} catch(e) {
		displayMessageBox('Invalid URL. The URL of the pull request must follow the format: https://github.com/ORGANIZATION/PROJECT/pull/X');
		return;
	}
	
	clearEditor();
	startLoadingState();
	
	var partitionsURL = pullURL + 'partitions/';
	$('#partition_tree').jstree(true).settings.core.data = {
				"url" : partitionsURL,
				"dataType" : "json",
				"success": function(data, textStatus, jqXHR) {
				},
				"error": function(jqXHR, textStatus, errorThrown) { 
					displayMessageBox(jqXHR.responseText);
					clearTree();
				},
				"complete": function(data_jqXHR, textStatus, jqXHR_errorThrown) {
					stopLoadingState();
				}
	};
	$('#partition_tree').jstree(true).refresh();
	
	if (window.location.pathname !== pullURL) {
		window.history.pushState(null, '', pullURL);
	}
};

var initHeaderButtons = function() {
	$('#pull_request_url_input').keyup(function(event) {
		if(event.keyCode == 13) { // Enter/Return key
			$("#partition_button").click();
		}
	});
	
	$('#partition_button').click(partitionPullRequest);
	
	$('#about_button').click(function() {
		if ($('#about_div').is(":hidden")) {
			$('#about_div').slideDown("slow");
		} else {
			$('#about_div').slideUp("fast");
		}
	});
	
	$('#faq_button').click(function() {
		if ($('#faq_div').is(":hidden")) {
			$('#faq_div').fadeIn("slow");
		} else {
			$('#faq_div').fadeOut("fast");
		}
	});
};

var initAboutBox = function() {
	$('#about_close_button').click(function() {
		$('#about_div').slideUp("fast");
	});
};

var initFaqBox = function() {
	$('#faq_close_button').click(function() {
		$('#faq_div').fadeOut("fast");
	});
	
	$('.faq_question_header').click(function() {
		$(this).next().slideToggle("fast");
	});
};

var initMessageBox = function() {
	var msgBoxCloseHandler = function(e) {
		if (e.target === this) {
			$('#msgbox_div').css('display', 'none');
		}
	}
	$('#msgbox_close_button').click(msgBoxCloseHandler);
	$('#msgbox_div').click(msgBoxCloseHandler);
	$(document).keyup(function(e) {
		if (e.keyCode == 27) {
			$('#msgbox_close_button').click();
		}
	});
	
	$(document).ajaxError(function(event, jqXHR, settings, thrownError) {
		displayMessageBox(jqXHR.responseText);
	});
};

var initWaitCursorCallbacks = function() {
	$(document).ajaxStart(function() {
		$('html').addClass('waitCursor');
	});
	$(document).ajaxStop(function() {
		$('html').removeClass('waitCursor');
	});
};

var parseURL = function(url) {
	var parser = document.createElement('a');
	parser.href = url;
	return parser;
	// Given "http://example.com:3000/pathname/?search=test#hash"
	// parser.protocol; // => "http:"
	// parser.hostname; // => "example.com"
	// parser.port;     // => "3000"
	// parser.pathname; // => "/pathname/"
	// parser.search;   // => "?search=test"
	// parser.hash;     // => "#hash"
	// parser.host;     // => "example.com:3000"
};

var handleURLState = function() {
	// If a pull request is in the URL, update pull url path bar and partition it.
	if (window.location.pathname !== '/') {
		$('#pull_request_url_input').val(jccURLToGitHubURL(window.location.pathname));
		$('#partition_button').click();
		//~ FIXME Loading message is not shown automatically when clicking the button here programatically
		clearTree('Loading...');
	}
};

$(document).ready(function() {
	resizeDivs();
	initPartitionTree();
	initCodeEditor();
	initHeaderButtons();
	initAboutBox();
	initFaqBox();
	initMessageBox();
	initWaitCursorCallbacks();
	$(window).trigger('resize');
	handleURLState();
});

$(window).resize(onResize);
