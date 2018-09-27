

/*
*  input.js
*
*  All javascript needed for ACF to work
*
*  @type	awesome
*  @date	1/08/13
*
*  @param	N/A
*  @return	N/A
*/ 

var ba = {
	
	// vars
	ajaxurl				:	'',
	admin_url			:	'',
	wp_version			:	'',
	post_id				:	0,
	nonce				:	'',
	l10n				:	null,
	o					:	null,
	
	// helper functions
	helpers				:	{
		get_atts		: 	null,
		version_compare	:	null,
		uniqid			:	null,
		sortable		:	null,
		add_message		:	null,
		is_clone_field	:	null,
		url_to_object	:	null
	},
	
	
	// modules
	validation			:	null,
	conditional_logic	:	null,
	media				:	null,
	
	
	// fields
	fields				:	{
		date_picker		:	null,
		color_picker	:	null,
		Image			:	null,
		file			:	null,
		wysiwyg			:	null,
		gallery			:	null,
		relationship	:	null
	}
};

(function($){
	
	
	/*
	*  ba.helpers.isset
	*
	*  description
	*
	*  @type	function
	*  @date	20/07/13
	*
	*  @param	{mixed}		arguments
	*  @return	{boolean}	
	*/
	
	ba.helpers.isset = function(){
		
		var a = arguments,
	        l = a.length,
	        c = null,
	        undef;
		
	    if (l === 0) {
	        throw new Error('Empty isset');
	    }
		
		c = a[0];
		
	    for (i = 1; i < l; i++) {
	    	
	        if (a[i] === undef || c[ a[i] ] === undef) {
	            return false;
	        }
	        
	        c = c[ a[i] ];
	        
	    }
	    
	    return true;
			
	};
	
	
	/*
	*  ba.helpers.get_atts
	*
	*  description
	*
	*  @type	function
	*  @date	1/06/13
	*
	*  @param	{el}		$el
	*  @return	{object}	atts
	*/
	
	ba.helpers.get_atts = function( $el ){
		
		var atts = {};
		
		$.each( $el[0].attributes, function( index, attr ) {
        	
        	if( attr.name.substr(0, 5) == 'data-' )
        	{
	        	atts[ attr.name.replace('data-', '') ] = attr.value;
        	}
        });
        
        return atts;
			
	};
        
           
	/**
	 * Simply compares two string version values.
	 * 
	 * Example:
	 * versionCompare('1.1', '1.2') => -1
	 * versionCompare('1.1', '1.1') =>  0
	 * versionCompare('1.2', '1.1') =>  1
	 * versionCompare('2.23.3', '2.22.3') => 1
	 * 
	 * Returns:
	 * -1 = left is LOWER than right
	 *  0 = they are equal
	 *  1 = left is GREATER = right is LOWER
	 *  And FALSE if one of input versions are not valid
	 *
	 * @function
	 * @param {String} left  Version #1
	 * @param {String} right Version #2
	 * @return {Integer|Boolean}
	 * @author Alexey Bass (albass)
	 * @since 2011-07-14
	 */
	 
	ba.helpers.version_compare = function(left, right)
	{
	    if (typeof left + typeof right != 'stringstring')
	        return false;
	    
	    var a = left.split('.')
	    ,   b = right.split('.')
	    ,   i = 0, len = Math.max(a.length, b.length);
	        
	    for (; i < len; i++) {
	        if ((a[i] && !b[i] && parseInt(a[i]) > 0) || (parseInt(a[i]) > parseInt(b[i]))) {
	            return 1;
	        } else if ((b[i] && !a[i] && parseInt(b[i]) > 0) || (parseInt(a[i]) < parseInt(b[i]))) {
	            return -1;
	        }
	    }
	    
	    return 0;
	};
	
	
	/*
	*  Helper: uniqid
	*
	*  @description: 
	*  @since: 3.5.8
	*  @created: 17/01/13
	*/
	
	ba.helpers.uniqid = function()
    {
    	var newDate = new Date;
    	return newDate.getTime();
    };
    
    
    /*
	*  Helper: url_to_object
	*
	*  @description: 
	*  @since: 4.0.0
	*  @created: 17/01/13
	*/
	
    ba.helpers.url_to_object = function( url ){
	    
	    // vars
	    var obj = {},
	    	pairs = url.split('&');
	    
	    
		for( i in pairs )
		{
		    var split = pairs[i].split('=');
		    obj[decodeURIComponent(split[0])] = decodeURIComponent(split[1]);
		}
		
		return obj;
	    
    };
    
	
	/*
	*  Sortable Helper
	*
	*  @description: keeps widths of td's inside a tr
	*  @since 3.5.1
	*  @created: 10/11/12
	*/
	
	ba.helpers.sortable = function(e, ui)
	{
		ui.children().each(function(){
			$(this).width($(this).width());
		});
		return ui;
	};
	
	
	/*
	*  is_clone_field
	*
	*  @description: 
	*  @since: 3.5.8
	*  @created: 17/01/13
	*/
	
	ba.helpers.is_clone_field = function( input )
	{
		if( input.attr('name') && input.attr('name').indexOf('[bacloneindex]') != -1 )
		{
			return true;
		}
		
		return false;
	};
	
	
	/*
	*  ba.helpers.add_message
	*
	*  @description: 
	*  @since: 3.2.7
	*  @created: 10/07/2012
	*/
	
	ba.helpers.add_message = function( message, div ){
		
		var message = $('<div class="ba-message-wrapper"><div class="message updated"><p>' + message + '</p></div></div>');
		
		div.prepend( message );
		
		setTimeout(function(){
			
			message.animate({
				opacity : 0
			}, 250, function(){
				message.remove();
			});
			
		}, 1500);
	};
	
	
	/*
	*  Exists
	*
	*  @description: returns true / false		
	*  @created: 1/03/2011
	*/
	
	$.fn.exists = function()
	{
		return $(this).length>0;
	};
	
	
	/*
	*  3.5 Media
	*
	*  @description: 
	*  @since: 3.5.7
	*  @created: 16/01/13
	*/
	
	ba.media = {
	
		div : null,
		frame : null,
		render_timout : null,
		
		clear_frame : function(){
			
			// validate
			if( !this.frame )
			{
				return;
			}
			
			
			// detach
			this.frame.detach();
			this.frame.dispose();
			
			
			// reset var
			this.frame = null;
			
		},
		type : function(){
			
			// default
			var type = 'thickbox';
			
			
			// if wp exists
			if( typeof wp !== 'undefined' )
			{
				type = 'backbone';
			}
			
			
			// return
			return type;
			
		},
		init : function(){
			
			// validate
			if( this.type() !== 'backbone' )
			{
				return false;
			}
			
			
			// validate prototype
			if( ! ba.helpers.isset(wp, 'media', 'view', 'AttachmentCompat', 'prototype') )
			{
				return false;	
			}
			
			
			// vars
			var _prototype = wp.media.view.AttachmentCompat.prototype;
			
			
			// orig
			_prototype.orig_render = _prototype.render;
			_prototype.orig_dispose = _prototype.dispose;
			
			
			// update class
			_prototype.className = 'compat-item ba_postbox no_box';
			
			
			// modify render
			_prototype.render = function() {
				
				// reference
				var _this = this;
				
				
				// validate
				if( _this.ignore_render )
				{
					return this;	
				}
				
				
				// run the old render function
				this.orig_render();
				
				
				// add button
				setTimeout(function(){
					
					// vars
					var $media_model = _this.$el.closest('.media-modal');
					
					
					// is this an edit only modal?
					if( $media_model.hasClass('ba-media-modal') )
					{
						return;	
					}
					
					
					// does button already exist?
					if( $media_model.find('.media-frame-router .ba-expand-details').exists() )
					{
						return;	
					}
					
					
					// create button
					var button = $([
						'<a href="#" class="ba-expand-details">',
							'<span class="icon"></span>',
							'<span class="is-closed">' + ba.l10n.core.expand_details +  '</span>',
							'<span class="is-open">' + ba.l10n.core.collapse_details +  '</span>',
						'</a>'
					].join('')); 
					
					
					// add events
					button.on('click', function( e ){
						
						e.preventDefault();
						
						if( $media_model.hasClass('ba-expanded') )
						{
							$media_model.removeClass('ba-expanded');
						}
						else
						{
							$media_model.addClass('ba-expanded');
						}
						
					});
					
					
					// append
					$media_model.find('.media-frame-router').append( button );
						
				
				}, 0);
				
				
				// setup fields
				// The clearTimout is needed to prevent many setup functions from running at the same time
				clearTimeout( ba.media.render_timout );
				ba.media.render_timout = setTimeout(function(){

					$(document).trigger( 'ba/setup_fields', [ _this.$el ] );
					
				}, 50);

				
				// return based on the origional render function
				return this;
			};
			
			
			// modify dispose
			_prototype.dispose = function() {
				
				// remove
				$(document).trigger('ba/remove_fields', [ this.$el ]);
				
				
				// run the old render function
				this.orig_dispose();
				
			};
			
			
			// override save
			_prototype.save = function( event ) {
			
				var data = {},
					names = {};
				
				if ( event )
					event.preventDefault();
					
					
				_.each( this.$el.serializeArray(), function( pair ) {
				
					// initiate name
					if( pair.name.slice(-2) === '[]' )
					{
						// remove []
						pair.name = pair.name.replace('[]', '');
						
						
						// initiate counter
						if( typeof names[ pair.name ] === 'undefined'){
							
							names[ pair.name ] = -1;
							//console.log( names[ pair.name ] );
							
						}
						
						
						names[ pair.name ]++
						
						pair.name += '[' + names[ pair.name ] +']';
						
						
					}
 
					data[ pair.name ] = pair.value;
				});
 
				this.ignore_render = true;
				this.model.saveCompat( data );
				
			};
		}
	};
	
	
	/*
	*  Conditional Logic Calculate
	*
	*  @description: 
	*  @since 3.5.1
	*  @created: 15/10/12
	*/
	
	ba.conditional_logic = {
		
		items : [],
		
		init : function(){
			
			// reference
			var _this = this;
			
			
			// events
			$(document).on('change', '.field input, .field textarea, .field select', function(){
				
				// preview hack
				if( $('#ba-has-changed').exists() )
				{
					$('#ba-has-changed').val(1);
				}
				
				_this.change( $(this) );
				
			});
			
			
			$(document).on('ba/setup_fields', function(e, el){
				
				//console.log('ba/setup_fields calling ba.conditional_logic.refresh()');
				_this.refresh( $(el) );
				
			});
			
			//console.log('ba.conditional_logic.init() calling ba.conditional_logic.refresh()');
			_this.refresh();
			
		},
		change : function( $el ){
			
			//console.log('change %o', $el);
			// reference
			var _this = this;
			
			
			// vars
			var $field = $el.closest('.field'),
				key = $field.attr('data-field_key');
			
			
			// loop through items and find rules where this field key is a trigger
			$.each(this.items, function( k, item ){
				
				$.each(item.rules, function( k2, rule ){
					
					// compare rule against the changed $field
					if( rule.field == key )
					{
						_this.refresh_field( item );
					}
					
				});
				
			});
			
		},
		
		refresh_field : function( item ){
			
			//console.log( 'refresh_field: %o ', item );
			// reference
			var _this = this;
			
			
			// vars
			var $targets	=	$('.field_key-' + item.field);

			
			// may be multiple targets (sub fields)
			$targets.each(function(){
				
				//console.log('target %o', $(this));
				
				// vars
				var show = true;
				
				
				// if 'any' was selected, start of as false and any match will result in show = true
				if( item.allorany == 'any' )
				{
					show = false;
				}
				
				
				// vars
				var $target		=	$(this),
					hide_all	=	true;
				
				
				// loop through rules
				$.each(item.rules, function( k2, rule ){
					
					// vars
					var $toggle = $('.field_key-' + rule.field);
					
					
					// are any of $toggle a sub field?
					if( $toggle.hasClass('sub_field') )
					{
						// toggle may be a sibling sub field.
						// if so ,show an empty td but keep the column
						$toggle = $target.siblings('.field_key-' + rule.field);
						hide_all = false;
						
						
						// if no toggle was found, we need to look at parent sub fields.
						// if so, hide the entire column
						if( ! $toggle.exists() )
						{
							// loop through all the parents that could contain sub fields
							$target.parents('tr').each(function(){
								
								// attempt to update $toggle to this parent sub field
								$toggle = $(this).find('.field_key-' + rule.field)
								
								// if the parent sub field actuallly exists, great! Stop the loop
								if( $toggle.exists() )
								{
									return false;
								}
								
							});

							hide_all = true;
						}
						
					}
					
					
					// if this sub field is within a flexible content layout, hide the entire column because 
					// there will never be another row added to this table
					var parent = $target.parent('tr').parent().parent('table').parent('.layout');
					if( parent.exists() )
					{
						hide_all = true;
						
						if( $target.is('th') && $toggle.is('th') )
						{
							$toggle = $target.closest('.layout').find('td.field_key-' + rule.field);
						}

					}
					
					// if this sub field is within a repeater field which has a max row of 1, hide the entire column because 
					// there will never be another row added to this table
					var parent = $target.parent('tr').parent().parent('table').parent('.repeater');
					if( parent.exists() && parent.attr('data-max_rows') == '1' )
					{
						hide_all = true;
						
						if( $target.is('th') && $toggle.is('th') )
						{
							$toggle = $target.closest('table').find('td.field_key-' + rule.field);
						}

					}
					
					
					var calculate = _this.calculate( rule, $toggle, $target );
					
					if( item.allorany == 'all' )
					{
						if( calculate == false )
						{
							show = false;
							
							// end loop
							return false;
						}
					}
					else
					{
						if( calculate == true )
						{
							show = true;
							
							// end loop
							return false;
						}
					}
					
				});
				// $.each(item.rules, function( k2, rule ){
				
				
				// clear classes
				$target.removeClass('ba-conditional_logic-hide ba-conditional_logic-show ba-show-blank');
				
				
				// hide / show field
				if( show )
				{
					// remove "disabled"
					$target.find('input, textarea, select').removeAttr('disabled');
					
					$target.addClass('ba-conditional_logic-show');
					
					// hook
					$(document).trigger('ba/conditional_logic/show', [ $target, item ]);
					
				}
				else
				{
					// add "disabled"
					$target.find('input, textarea, select').attr('disabled', 'disabled');
					
					$target.addClass('ba-conditional_logic-hide');
					
					if( !hide_all )
					{
						$target.addClass('ba-show-blank');
					}
					
					// hook
					$(document).trigger('ba/conditional_logic/hide', [ $target, item ]);
				}
				
				
			});
			
		},
		
		refresh : function( $el ){
			
			// defaults
			$el = $el || $('body');
			
			
			// reference
			var _this = this;
			
			
			// loop through items and find rules where this field key is a trigger
			$.each(this.items, function( k, item ){
				
				$.each(item.rules, function( k2, rule ){
					
					// is this field within the $el
					// this will increase performance by ignoring conditional logic outside of this newly appended element ($el)
					if( ! $el.find('.field[data-field_key="' + item.field + '"]').exists() )
					{
						return;
					}
					
					_this.refresh_field( item );
					
				});
				
			});
			
		},
		
		calculate : function( rule, $toggle, $target ){
			
			// vars
			var r = false;
			

			// compare values
			if( $toggle.hasClass('field_type-true_false') || $toggle.hasClass('field_type-checkbox') || $toggle.hasClass('field_type-radio') )
			{
				var exists = $toggle.find('input[value="' + rule.value + '"]:checked').exists();
				
				
				if( rule.operator == "==" )
				{
					if( exists )
					{
						r = true;
					}
				}
				else
				{
					if( ! exists )
					{
						r = true;
					}
				}
				
			}
			else
			{
				// get val and make sure it is an array
				var val = $toggle.find('input, textarea, select').last().val();
				
				if( ! $.isArray(val) )
				{
					val = [ val ];
				}
				

				if( rule.operator == "==" )
				{
					if( $.inArray(rule.value, val) > -1 )
					{
						r = true;
					}
				}
				else
				{
					if( $.inArray(rule.value, val) < 0 )
					{
						r = true;
					}
				}
				
			}
			
			
			// return
			return r;
			
		}
		
	};
	
	
	
	
		
	/*
	*  Document Ready
	*
	*  @description: 
	*  @since: 3.5.8
	*  @created: 17/01/13
	*/
	
	$(document).ready(function(){
		
		
		// conditional logic
		ba.conditional_logic.init();
		
		
		// fix for older options page add-on
		$('.ba_postbox > .inside > .options').each(function(){
			
			$(this).closest('.ba_postbox').addClass( $(this).attr('data-layout') );
			
		});
		
		
		// Remove 'field_123' from native custom field metabox
		$('#metakeyselect option[value^="field_"]').remove();
		
	
	});
	
	
	/*
	*  window load
	*
	*  @description: 
	*  @since: 3.5.5
	*  @created: 22/12/12
	*/
	
	$(window).on('load', function(){
		
		// init
		ba.media.init();
		
		
		setTimeout(function(){
			
			// Hack for CPT without a content editor
			try
			{
				// post_id may be string (user_1) and therefore, the uploaded image cannot be attached to the post
				if( $.isNumeric(ba.o.post_id) )
				{
					wp.media.view.settings.post.id = ba.o.post_id;
				}
				
			} 
			catch(e)
			{
				// one of the objects was 'undefined'...
			}
			
			
			// setup fields
			$(document).trigger('ba/setup_fields', [ $('#poststuff') ]);
			
		}, 10);
		
	});
	
	
	/*
	*  Gallery field Add-on Fix
	*
	*  Gallery field v1.0.0 required some data in the ba object.
	*  Now not required, but older versions of gallery field need this.
	*
	*  @type	object
	*  @date	1/08/13
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	ba.fields.gallery = {
		add : function(){},
		edit : function(){},
		update_count : function(){},
		hide_selected_items : function(){},
		text : {
			title_add : "Select Images"
		}
	};
	
		
	
})(jQuery);

(function($){
	
	
	/*
	*  ba.screen
	*
	*  Data used by AJAX to hide / show field groups
	*
	*  @type	object
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	ba.screen = {
		action 			:	'ba/location/match_field_groups_ajax',
		post_id			:	0,
		page_template	:	0,
		page_parent		:	0,
		page_type		:	0,
		post_category	:	0,
		post_format		:	0,
		taxonomy		:	0,
		lang			:	0,
		nonce			:	0
	};
	
	
	/*
	*  Document Ready
	*
	*  Updates ba.screen with more data
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).ready(function(){
		return;
		
		// update post_id
		ba.screen.post_id = ba.o.post_id;
		ba.screen.nonce = ba.o.nonce;
		
		
		// MPML
		if( $('#icl-als-first').length > 0 )
		{
			var href = $('#icl-als-first').children('a').attr('href'),
				regex = new RegExp( "lang=([^&#]*)" ),
				results = regex.exec( href );
			
			// lang
			ba.screen.lang = results[1];
			
		}
		
	});
	
	
	/*
	*  ba/update_field_groups
	*
	*  finds the new id's for metaboxes and show's hides metaboxes
	*
	*  @type	event
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('ba/update_field_groups', function(){
		
		// Only for a post.
		// This is an attempt to stop the action running on the options page add-on.
		if( ! ba.screen.post_id || ! $.isNumeric(ba.screen.post_id) )
		{
			return false;	
		}
		
		
		$.ajax({
			url: ajaxurl,
			data: ba.screen,
			type: 'post',
			dataType: 'json',
			success: function(result){
				
				// validate
				if( !result )
				{
					return false;
				}
				
				
				// hide all metaboxes
				$('.ba_postbox').addClass('ba-hidden');
				$('.ba_postbox-toggle').addClass('ba-hidden');
		
				
				// dont bother loading style or html for inputs
				if( result.length == 0 )
				{
					return false;
				}
				
				
				// show the new postboxes
				$.each(result, function(k, v) {
					
					
					// vars
					var $el = $('#ba_' + v),
						$toggle = $('#adv-settings .ba_postbox-toggle[for="ba_' + v + '-hide"]');
					
					
					// classes
					$el.removeClass('ba-hidden hide-if-js');
					$toggle.removeClass('ba-hidden');
					$toggle.find('input[type="checkbox"]').attr('checked', 'checked');
					
					
					// load fields if needed
					$el.find('.ba-replace-with-fields').each(function(){
						
						var $replace = $(this);
						
						$.ajax({
							url			:	ajaxurl,
							data		:	{
								action	:	'ba/post/render_fields',
								ba_id	:	v,
								post_id	:	ba.o.post_id,
								nonce	:	ba.o.nonce
							},
							type		:	'post',
							dataType	:	'html',
							success		:	function( html ){
							
								$replace.replaceWith( html );
								
								$(document).trigger('ba/setup_fields', $el);
								
							}
						});
						
					});
				});
				
				
				// load style
				$.ajax({
					url			:	ajaxurl,
					data		:	{
						action	:	'ba/post/get_style',
						ba_id	:	result[0],
						nonce	:	ba.o.nonce
					},
					type		: 'post',
					dataType	: 'html',
					success		: function( result ){
					
						$('#ba_style').html( result );
						
					}
				});
				
				
				
			}
		});
	});

	
	/*
	*  Events
	*
	*  Updates ba.screen with more data and triggers the update event
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('change', '#page_template', function(){
		
		ba.screen.page_template = $(this).val();
		
		$(document).trigger('ba/update_field_groups');
	    
	});
	
	
	$(document).on('change', '#parent_id', function(){
		
		var val = $(this).val();
		
		
		// set page_type / page_parent
		if( val != "" )
		{
			ba.screen.page_type = 'child';
			ba.screen.page_parent = val;
		}
		else
		{
			ba.screen.page_type = 'parent';
			ba.screen.page_parent = 0;
		}
		
		
		$(document).trigger('ba/update_field_groups');
	    
	});

	
	$(document).on('change', '#post-formats-select input[type="radio"]', function(){
		
		var val = $(this).val();
		
		if( val == '0' )
		{
			val = 'standard';
		}
		
		ba.screen.post_format = val;
		
		$(document).trigger('ba/update_field_groups');
		
	});	
	
	
	function _sync_taxonomy_terms() {
		
		// vars
		var values = [];
		
		
		$('.categorychecklist input:checked, .ba-taxonomy-field input:checked, .ba-taxonomy-field option:selected').each(function(){
			
			// validate
			if( $(this).is(':hidden') || $(this).is(':disabled') )
			{
				return;
			}
			
			
			// validate media popup
			if( $(this).closest('.media-frame').exists() )
			{
				return;
			}
			
			
			// validate ba
			if( $(this).closest('.ba-taxonomy-field').exists() )
			{
				if( $(this).closest('.ba-taxonomy-field').attr('data-load_save') == '0' )
				{
					return;
				}
			}
			
			
			// append
			if( values.indexOf( $(this).val() ) === -1 )
			{
				values.push( $(this).val() );
			}
			
		});

		
		// update screen
		ba.screen.post_category = values;
		ba.screen.taxonomy = values;

		
		// trigger change
		$(document).trigger('ba/update_field_groups');
			
	}
	
	
	$(document).on('change', '.categorychecklist input, .ba-taxonomy-field input, .ba-taxonomy-field select', function(){
		
		// a taxonomy field may trigger this change event, however, the value selected is not
		// actually a term relatinoship, it is meta data
		if( $(this).closest('.ba-taxonomy-field').exists() )
		{
			if( $(this).closest('.ba-taxonomy-field').attr('data-save') == '0' )
			{
				return;
			}
		}
		
		
		// this may be triggered from editing an imgae in a popup. Popup does not support correct metaboxes so ignore this
		if( $(this).closest('.media-frame').exists() )
		{
			return;
		}
		
		
		// set timeout to fix issue with chrome which does not register the change has yet happened
		setTimeout(function(){
			
			_sync_taxonomy_terms();
		
		}, 1);
		
		
	});
	
	
	
	
})(jQuery);

(function($){
	
	/*
	*  Color Picker
	*
	*  jQuery functionality for this field type
	*
	*  @type	object
	*  @date	20/07/13
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	var _cp = ba.fields.color_picker = {
		
		$el : null,
		$input : null,
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find input
			this.$input = this.$el.find('input[type="text"]');
			
			
			// return this for chaining
			return this;
			
		},
		init : function(){
			
			// vars (reference)
			var $input = this.$input;
			
			
			// is clone field?
			if( ba.helpers.is_clone_field($input) )
			{
				return;
			}
			
			
			this.$input.wpColorPicker();
			
			
			
		}
	};
	
	
	/*
	*  ba/setup_fields
	*
	*  run init function on all elements for this field
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/setup_fields', function(e, el){
		
		$(el).find('.ba-color_picker').each(function(){
			
			_cp.set({ $el : $(this) }).init();
			
		});
		
	});
		

})(jQuery);

(function($){
	
	/*
	*  Date Picker
	*
	*  static model for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	ba.fields.date_picker = {
		
		$el : null,
		$input : null,
		$hidden : null,
		
		o : {},
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find input
			this.$input = this.$el.find('input[type="text"]');
			this.$hidden = this.$el.find('input[type="hidden"]');
			
			
			// get options
			this.o = ba.helpers.get_atts( this.$el );
			
			
			// return this for chaining
			return this;
			
		},
		init : function(){

			// is clone field?
			if( ba.helpers.is_clone_field(this.$hidden) )
			{
				return;
			}
			
			
			// get and set value from alt field
			this.$input.val( this.$hidden.val() );
			
			
			// create options
			var options = $.extend( {}, ba.l10n.date_picker, { 
				dateFormat		:	this.o.save_format,
				altField		:	this.$hidden,
				altFormat		:	this.o.save_format,
				changeYear		:	true,
				yearRange		:	"-100:+100",
				changeMonth		:	true,
				showButtonPanel	:	true,
				firstDay		:	this.o.first_day
			});
			
			
			// add date picker
			this.$input.addClass('active').datepicker( options );
			
			
			// now change the format back to how it should be.
			this.$input.datepicker( "option", "dateFormat", this.o.display_format );
			
			
			// wrap the datepicker (only if it hasn't already been wrapped)
			if( $('body > #ui-datepicker-div').length > 0 )
			{
				$('#ui-datepicker-div').wrap('<div class="ui-ba" />');
			}
			
		},
		blur : function(){
			
			if( !this.$input.val() )
			{
				this.$hidden.val('');
			}
			
		}
		
	};
	
	
	/*
	*  ba/setup_fields
	*
	*  run init function on all elements for this field
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/setup_fields', function(e, el){
		
		$(el).find('.ba-date_picker').each(function(){
			
			ba.fields.date_picker.set({ $el : $(this) }).init();
			
		});
		
	});
	
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	$(document).on('blur', '.ba-date_picker input[type="text"]', function( e ){
		
		ba.fields.date_picker.set({ $el : $(this).parent() }).blur();
					
	});
	

})(jQuery);

(function($){
	
	/*
	*  File
	*
	*  static model for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	
	// reference
	var _media = ba.media;
	
	
	ba.fields.file = {
		
		$el : null,
		$input : null,
		
		o : {},
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find input
			this.$input = this.$el.find('input[type="hidden"]');
			
			
			// get options
			this.o = ba.helpers.get_atts( this.$el );
			
			
			// multiple?
			this.o.multiple = this.$el.closest('.repeater').exists() ? true : false;
			
			
			// wp library query
			this.o.query = {};
			
			
			// library
			if( this.o.library == 'uploadedTo' )
			{
				this.o.query.uploadedTo = ba.o.post_id;
			}
			
			
			// return this for chaining
			return this;
			
		},
		init : function(){

			// is clone field?
			if( ba.helpers.is_clone_field(this.$input) )
			{
				return;
			}
					
		},
		add : function( file ){
			
			// this function must reference a global div variable due to the pre WP 3.5 uploader
			// vars
			var div = _media.div;
			
			
			// set atts
			div.find('.ba-file-icon').attr( 'src', file.icon );
		 	div.find('.ba-file-title').text( file.title );
		 	div.find('.ba-file-name').text( file.name ).attr( 'href', file.url );
		 	div.find('.ba-file-size').text( file.size );
			div.find('.ba-file-value').val( file.id ).trigger('change');
		 	
		 	
		 	// set div class
		 	div.addClass('active');
		 	
		 	
		 	// validation
			div.closest('.field').removeClass('error');
	
		},
		
		new_frame: function( attributes ){
			
			// set global var
			_media.div = this.$el;
			

			// clear the frame
			_media.clear_frame();
			
			
			// vars
			attributes.states = [];
			
			// append states
			attributes.states.push(
				new wp.media.controller.Library({
					library		:	wp.media.query( this.o.query ),
					multiple	:	attributes.multiple,
					title		:	attributes.title,
					priority	:	20,
					filterable	:	'all'
				})
			);
			
			
			// edit image functionality (added in WP 3.9)
			if( ba.helpers.isset(wp, 'media', 'controller', 'EditImage') ) {
				
				attributes.states.push( new wp.media.controller.EditImage() );
				
			}
			
			
			// Create the media frame
			_media.frame = wp.media( attributes );
			
			
			// edit image view
			// source: media-views.js:2410 editImageContent()
			_media.frame.on('content:render:edit-image', function(){
				
				var image = this.state().get('image'),
					view = new wp.media.view.EditImage( { model: image, controller: this } ).render();
	
				this.content.set( view );
	
				// after creating the wrapper view, load the actual editor via an ajax call
				view.loadEditor();
				
			}, _media.frame);
			
			
			// update toolbar button
			_media.frame.on( 'toolbar:create:select', function( toolbar ) {
				
				toolbar.view = new wp.media.view.Toolbar.Select({
					text: attributes.button.text,
					controller: this
				});
				
			}, _media.frame );
			
			
			// return
			return _media.frame;
			
		},
		
		edit : function(){
			
			// vars
			var id = this.$input.val();
			
			
			// create frame
			this.new_frame({
				title		:	ba.l10n.file.edit,
				multiple	:	false,
				button		:	{ text : ba.l10n.file.update }
			});
						
			
			// open
			_media.frame.on('open',function() {
				
				// set to browse
				if( _media.frame.content._mode != 'browse' )
				{
					_media.frame.content.mode('browse');
				}
				
				
				// add class
				_media.frame.$el.closest('.media-modal').addClass('ba-media-modal ba-expanded');
					
				
				// set selection
				var selection	=	_media.frame.state().get('selection'),
					attachment	=	wp.media.attachment( id );
				
				
				// to fetch or not to fetch
				if( $.isEmptyObject(attachment.changed) )
				{
					attachment.fetch();
				}
				

				selection.add( attachment );
						
			});
			
			
			// close
			_media.frame.on('close',function(){
			
				// remove class
				_media.frame.$el.closest('.media-modal').removeClass('ba-media-modal');
				
			});
			
							
			// Finally, open the modal
			ba.media.frame.open();
			
		},
		remove : function()
		{
			
			// set atts
			this.$el.find('.ba-file-icon').attr( 'src', '' );
			this.$el.find('.ba-file-title').text( '' );
		 	this.$el.find('.ba-file-name').text( '' ).attr( 'href', '' );
		 	this.$el.find('.ba-file-size').text( '' );
			this.$el.find('.ba-file-value').val( '' ).trigger('change');
			
			
			// remove class
			this.$el.removeClass('active');
			
		},
		popup : function()
		{
			// reference
			var t = this;
			
			
			// create frame
			this.new_frame({
				title		:	ba.l10n.file.select,
				multiple	:	t.o.multiple,
				button		:	{ text : ba.l10n.file.select }
			});
			
			
			// customize model / view
			ba.media.frame.on('content:activate', function(){
				
				// vars
				var toolbar = null,
					filters = null;
					
				
				// populate above vars making sure to allow for failure
				try
				{
					toolbar = ba.media.frame.content.get().toolbar;
					filters = toolbar.get('filters');
				} 
				catch(e)
				{
					// one of the objects was 'undefined'... perhaps the frame open is Upload Files
					//console.log( e );
				}
				
				
				// validate
				if( !filters )
				{
					return false;
				}
				
				
				// no need for 'uploaded' filter
				if( t.o.library == 'uploadedTo' )
				{
					filters.$el.find('option[value="uploaded"]').remove();
					filters.$el.after('<span>' + ba.l10n.file.uploadedTo + '</span>')
					
					$.each( filters.filters, function( k, v ){
						
						v.props.uploadedTo = ba.o.post_id;
						
					});
				}
								
			});
			
			
			// When an image is selected, run a callback.
			ba.media.frame.on( 'select', function() {
				
				// get selected images
				selection = _media.frame.state().get('selection');
				
				if( selection )
				{
					var i = 0;
					
					selection.each(function(attachment){
	
				    	// counter
				    	i++;
				    	
				    	
				    	// select / add another file field?
				    	if( i > 1 )
						{
							// vars
							var $td			=	_media.div.closest('td'),
								$tr 		=	$td.closest('.row'),
								$repeater 	=	$tr.closest('.repeater'),
								key 		=	$td.attr('data-field_key'),
								selector	=	'td .ba-file-uploader:first';
								
							
							// key only exists for repeater v1.0.1 +
							if( key )
							{
								selector = 'td[data-field_key="' + key + '"] .ba-file-uploader';
							}
							
							
							// add row?
							if( ! $tr.next('.row').exists() )
							{
								$repeater.find('.add-row-end').trigger('click');
								
							}
							
							
							// update current div
							_media.div = $tr.next('.row').find( selector );
							
						}
												
						
				    	// vars
				    	var file = {
					    	id		:	attachment.id,
					    	title	:	attachment.attributes.title,
					    	name	:	attachment.attributes.filename,
					    	url		:	attachment.attributes.url,
					    	icon	:	attachment.attributes.icon,
					    	size	:	attachment.attributes.filesize
				    	};
				    	
				    	
				    	// add file to field
				        ba.fields.file.add( file );
				        
						
				    });
				    // selection.each(function(attachment){
				}
				// if( selection )
				
			});
			// ba.media.frame.on( 'select', function() {
					 
				
			// Finally, open the modal
			ba.media.frame.open();
				
			
			return false;
		}
		
	};
	
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('click', '.ba-file-uploader .ba-button-edit', function( e ){
		
		e.preventDefault();
		
		ba.fields.file.set({ $el : $(this).closest('.ba-file-uploader') }).edit();
			
	});
	
	$(document).on('click', '.ba-file-uploader .ba-button-delete', function( e ){
		
		e.preventDefault();
		
		ba.fields.file.set({ $el : $(this).closest('.ba-file-uploader') }).remove();
			
	});
	
	
	$(document).on('click', '.ba-file-uploader .add-file', function( e ){
		
		e.preventDefault();
		
		ba.fields.file.set({ $el : $(this).closest('.ba-file-uploader') }).popup();
		
	});
	

})(jQuery);

(function($){
	
	/*
	*  Location
	*
	*  static model for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	ba.fields.google_map = {
		
		$el : null,
		$input : null,
		
		o : {},
		api: {
			sensor:		false,
			libraries:	'places'
		},
		
		ready : false,
		geocoder : false,
		map : false,
		maps : {},
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find input
			this.$input = this.$el.find('.input-address');
			
			
			// get options
			this.o = ba.helpers.get_atts( this.$el );
			
			
			// get map
			if( this.maps[ this.o.id ] )
			{
				this.map = this.maps[ this.o.id ];
			}
			
			
			// return this for chaining
			return this;
			
		},
		init : function(){
			
			// geocode
			if( !this.geocoder )
			{
				this.geocoder = new google.maps.Geocoder();
			}
			
			
			// google maps is loaded and ready
			this.ready = true;
			
			
			// is clone field?
			if( ba.helpers.is_clone_field(this.$input) )
			{
				return;
			}
			
			this.render();
					
		},
		render : function(){
			
			// reference
			var _this	= this,
				_$el	= this.$el;
			
			
			// vars
			var args = {
        		zoom		: parseInt(this.o.zoom),
        		center		: new google.maps.LatLng(this.o.lat, this.o.lng),
        		mapTypeId	: google.maps.MapTypeId.ROADMAP
        	};
			
			// create map	        	
        	this.map = new google.maps.Map( this.$el.find('.canvas')[0], args);
	        
	        
	        // add search
			var autocomplete = new google.maps.places.Autocomplete( this.$el.find('.search')[0] );
			autocomplete.map = this.map;
			autocomplete.bindTo('bounds', this.map);
			
			
			// add dummy marker
	        this.map.marker = new google.maps.Marker({
		        draggable	: true,
		        raiseOnDrag	: true,
		        map			: this.map,
		    });
		    
		    
		    // add references
		    this.map.$el = this.$el;
		    
		    
		    // value exists?
		    var lat = this.$el.find('.input-lat').val(),
		    	lng = this.$el.find('.input-lng').val();
		    
		    if( lat && lng )
		    {
			    this.update( lat, lng ).center();
		    }
		    
		    
			// events
			google.maps.event.addListener(autocomplete, 'place_changed', function( e ) {
			    
			    // reference
			    var $el = this.map.$el;


			    // manually update address
			    var address = $el.find('.search').val();
			    $el.find('.input-address').val( address );
			    $el.find('.title h4').text( address );
			    
			    
			    // vars
			    var place = this.getPlace();
			    
			    
			    // validate
			    if( place.geometry )
			    {
			    	var lat = place.geometry.location.lat(),
						lng = place.geometry.location.lng();
						
						
				    _this.set({ $el : $el }).update( lat, lng ).center();
			    }
			    else
			    {
				    // client hit enter, manulaly get the place
				    _this.geocoder.geocode({ 'address' : address }, function( results, status ){
				    	
				    	// validate
						if( status != google.maps.GeocoderStatus.OK )
						{
							console.log('Geocoder failed due to: ' + status);
							return;
						}
						
						if( !results[0] )
						{
							console.log('No results found');
							return;
						}
						
						
						// get place
						place = results[0];
						
						var lat = place.geometry.location.lat(),
							lng = place.geometry.location.lng();
							
							
					    _this.set({ $el : $el }).update( lat, lng ).center();
					    
					});
			    }
			    
			});
		    
		    
		    google.maps.event.addListener( this.map.marker, 'dragend', function(){
		    	
		    	// reference
			    var $el = this.map.$el;
			    
			    
		    	// vars
				var position = this.map.marker.getPosition(),
					lat = position.lat(),
			    	lng = position.lng();
			    	
				_this.set({ $el : $el }).update( lat, lng ).sync();
			    
			});
			
			
			google.maps.event.addListener( this.map, 'click', function( e ) {
				
				// reference
			    var $el = this.$el;
			    
			    
				// vars
				var lat = e.latLng.lat(),
					lng = e.latLng.lng();
				
				
				_this.set({ $el : $el }).update( lat, lng ).sync();
			
			});

			
			
	        // add to maps
	        this.maps[ this.o.id ] = this.map;
	        
	        
		},
		
		update : function( lat, lng ){
			
			// vars
			var latlng = new google.maps.LatLng( lat, lng );
		    
		    
		    // update inputs
			this.$el.find('.input-lat').val( lat );
			this.$el.find('.input-lng').val( lng ).trigger('change');
			
			
		    // update marker
		    this.map.marker.setPosition( latlng );
		    
		    
			// show marker
			this.map.marker.setVisible( true );
		    
		    
	        // update class
	        this.$el.addClass('active');
	        
	        
	        // validation
			this.$el.closest('.field').removeClass('error');
			
			
	        // return for chaining
	        return this;
		},
		
		center : function(){
			
			// vars
			var position = this.map.marker.getPosition(),
				lat = this.o.lat,
				lng = this.o.lng;
			
			
			// if marker exists, center on the marker
			if( position )
			{
				lat = position.lat();
				lng = position.lng();
			}
			
			
			var latlng = new google.maps.LatLng( lat, lng );
				
			
			// set center of map
	        this.map.setCenter( latlng );
		},
		
		sync : function(){
			
			// reference
			var $el	= this.$el;
				
			
			// vars
			var position = this.map.marker.getPosition(),
				latlng = new google.maps.LatLng( position.lat(), position.lng() );
			
			
			this.geocoder.geocode({ 'latLng' : latlng }, function( results, status ){
				
				// validate
				if( status != google.maps.GeocoderStatus.OK )
				{
					console.log('Geocoder failed due to: ' + status);
					return;
				}
				
				if( !results[0] )
				{
					console.log('No results found');
					return;
				}
				
				
				// get location
				var location = results[0];
				
				
				// update h4
				$el.find('.title h4').text( location.formatted_address );

				
				// update input
				$el.find('.input-address').val( location.formatted_address ).trigger('change');
				
			});
			
			
			// return for chaining
	        return this;
		},
		
		locate : function(){
			
			// reference
			var _this	= this,
				_$el	= this.$el;
			
			
			// Try HTML5 geolocation
			if( ! navigator.geolocation )
			{
				alert( ba.l10n.google_map.browser_support );
				return this;
			}
			
			
			// show loading text
			_$el.find('.title h4').text(ba.l10n.google_map.locating + '...');
			_$el.addClass('active');
			
		    navigator.geolocation.getCurrentPosition(function(position){
		    	
		    	// vars
				var lat = position.coords.latitude,
			    	lng = position.coords.longitude;
			    	
				_this.set({ $el : _$el }).update( lat, lng ).sync().center();
				
			});

				
		},
		
		clear : function(){
			
			// update class
	        this.$el.removeClass('active');
			
			
			// clear search
			this.$el.find('.search').val('');
			
			
			// clear inputs
			this.$el.find('.input-address').val('');
			this.$el.find('.input-lat').val('');
			this.$el.find('.input-lng').val('');
			
			
			// hide marker
			this.map.marker.setVisible( false );
		},
		
		edit : function(){
			
			// update class
	        this.$el.removeClass('active');
			
			
			// clear search
			var val = this.$el.find('.title h4').text();
			
			
			this.$el.find('.search').val( val ).focus();
			
		},
		
		refresh : function(){
			
			// trigger resize on div
			google.maps.event.trigger(this.map, 'resize');
			
			// center map
			this.center();
			
		}
	
	};
	
	
	/*
	*  ba/setup_fields
	*
	*  run init function on all elements for this field
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/setup_fields', function(e, el){
		
		// reference
		var self = ba.fields.google_map;
			
			
		// vars
		var $fields = $(el).find('.ba-google-map');
		
		
		// validate
		if( ! $fields.exists() ) return false;
		
		
		// no google
		if( !ba.helpers.isset(window, 'google', 'load') ) {
			
			// load API
			$.getScript('https://www.google.com/jsapi', function(){
				
				// load maps
				google.load('maps', '3', { other_params: $.param(self.api), callback: function(){
			    	
			    	$fields.each(function(){
					
						ba.fields.google_map.set({ $el : $(this) }).init();
						
					});
			        
			    }});
			    
			});
			
			return false;
				
		}
		
		
		// no maps or places
		if( !ba.helpers.isset(window, 'google', 'maps', 'places') ) {
			
			google.load('maps', '3', { other_params: $.param(self.api), callback: function(){
				
				$fields.each(function(){
					
					ba.fields.google_map.set({ $el : $(this) }).init();
					
				});
		        
		    }});
			
			return false;
				
		}
		
		
		// google exists
		$fields.each(function(){
					
			ba.fields.google_map.set({ $el : $(this) }).init();
			
		});

		
		// return
		return true;
		
	});
	
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('click', '.ba-google-map .ba-sprite-remove', function( e ){
		
		e.preventDefault();
		
		ba.fields.google_map.set({ $el : $(this).closest('.ba-google-map') }).clear();
		
		$(this).blur();
		
	});
	
	
	$(document).on('click', '.ba-google-map .ba-sprite-locate', function( e ){
		
		e.preventDefault();
		
		ba.fields.google_map.set({ $el : $(this).closest('.ba-google-map') }).locate();
		
		$(this).blur();
		
	});
	
	$(document).on('click', '.ba-google-map .title h4', function( e ){
		
		e.preventDefault();
		
		ba.fields.google_map.set({ $el : $(this).closest('.ba-google-map') }).edit();
			
	});
	
	$(document).on('keydown', '.ba-google-map .search', function( e ){
		
		// prevent form from submitting
		if( e.which == 13 )
		{
		    return false;
		}
			
	});
	
	$(document).on('blur', '.ba-google-map .search', function( e ){
		
		// vars
		var $el = $(this).closest('.ba-google-map');
		
		
		// has a value?
		if( $el.find('.input-lat').val() )
		{
			$el.addClass('active');
		}
		
	});
	
	$(document).on('ba/fields/tab/show ba/conditional_logic/show', function( e, $field ){
		
		// validate
		if( ! ba.fields.google_map.ready )
		{
			return;
		}
		
		
		// validate
		if( $field.attr('data-field_type') == 'google_map' )
		{
			ba.fields.google_map.set({ $el : $field.find('.ba-google-map') }).refresh();
		}
		
	});

	

})(jQuery);

(function($){
	
	/*
	*  Image
	*
	*  static model for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	
	// reference
	var _media = ba.media;
	
	
	ba.fields.image = {
		
		$el : null,
		$input : null,
		
		o : {},
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find input
			this.$input = this.$el.find('input[type="hidden"]');
			
			
			// get options
			this.o = ba.helpers.get_atts( this.$el );
			
			
			// multiple?
			this.o.multiple = this.$el.closest('.repeater').exists() ? true : false;
			
			
			// wp library query
			this.o.query = {
				type : 'image'
			};
			
			
			// library
			if( this.o.library == 'uploadedTo' )
			{
				this.o.query.uploadedTo = ba.o.post_id;
			}
			
			
			// return this for chaining
			return this;
			
		},
		init : function(){

			// is clone field?
			if( ba.helpers.is_clone_field(this.$input) )
			{
				return;
			}
					
		},
		add : function( image ){
			
			// this function must reference a global div variable due to the pre WP 3.5 uploader
			// vars
			var div = _media.div;
			
			
			// set atts
			div.find('.ba-image-image').attr( 'src', image.url );
			div.find('.ba-image-value').val( image.id ).trigger('change');
		 	
			
		 	// set div class
		 	div.addClass('active');
		 	
		 	
		 	// validation
			div.closest('.field').removeClass('error');
	
		},
		
		new_frame: function( attributes ){
			
			// set global var
			_media.div = this.$el;
			

			// clear the frame
			_media.clear_frame();
			
			
			// vars
			attributes.states = [];
			
			
			// append states
			attributes.states.push(
				new wp.media.controller.Library({
					library		:	wp.media.query( this.o.query ),
					multiple	:	attributes.multiple,
					title		:	attributes.title,
					priority	:	20,
					filterable	:	'all'
				})
			);
			
			
			// edit image functionality (added in WP 3.9)
			if( ba.helpers.isset(wp, 'media', 'controller', 'EditImage') ) {
				
				attributes.states.push( new wp.media.controller.EditImage() );
				
			}
			
			
			// Create the media frame
			_media.frame = wp.media( attributes );
			
			
			// edit image view
			// source: media-views.js:2410 editImageContent()
			_media.frame.on('content:render:edit-image', function(){
				
				var image = this.state().get('image'),
					view = new wp.media.view.EditImage( { model: image, controller: this } ).render();
	
				this.content.set( view );
	
				// after creating the wrapper view, load the actual editor via an ajax call
				view.loadEditor();
				
			}, _media.frame);
			
			
			// update toolbar button
			_media.frame.on( 'toolbar:create:select', function( toolbar ) {
				
				toolbar.view = new wp.media.view.Toolbar.Select({
					text: attributes.button.text,
					controller: this
				});
				
			}, _media.frame );
			
			
			// return
			return _media.frame;
			
		},
		
		edit : function(){
			
			// vars
			var id = this.$input.val();
			
			
			// create frame
			this.new_frame({
				title		:	ba.l10n.image.edit,
				multiple	:	false,
				button		:	{ text : ba.l10n.image.update }
			});
						
			
			// open
			_media.frame.on('open',function() {
				
				// set to browse
				if( _media.frame.content._mode != 'browse' )
				{
					_media.frame.content.mode('browse');
				}
				
				
				// add class
				_media.frame.$el.closest('.media-modal').addClass('ba-media-modal ba-expanded');
					
				
				// set selection
				var selection	=	_media.frame.state().get('selection'),
					attachment	=	wp.media.attachment( id );
				
				
				// to fetch or not to fetch
				if( $.isEmptyObject(attachment.changed) )
				{
					attachment.fetch();
				}
				

				selection.add( attachment );
						
			});
			
			
			// close
			_media.frame.on('close',function(){
			
				// remove class
				_media.frame.$el.closest('.media-modal').removeClass('ba-media-modal');
				
			});
			
							
			// Finally, open the modal
			_media.frame.open();
			
		},
		remove : function()
		{
			
			// set atts
		 	this.$el.find('.ba-image-image').attr( 'src', '' );
			this.$el.find('.ba-image-value').val( '' ).trigger('change');
			
			
			// remove class
			this.$el.removeClass('active');
			
		},
		popup : function()
		{
			// reference
			var t = this;
			
			
			// create frame
			this.new_frame({
				title		:	ba.l10n.image.select,
				multiple	:	t.o.multiple,
				button		:	{ text : ba.l10n.image.select }
			});
			
			
			// customize model / view
			_media.frame.on('content:activate', function(){

				// vars
				var toolbar = null,
					filters = null;
					
				
				// populate above vars making sure to allow for failure
				try
				{
					toolbar = ba.media.frame.content.get().toolbar;
					filters = toolbar.get('filters');
				} 
				catch(e)
				{
					// one of the objects was 'undefined'... perhaps the frame open is Upload Files
					//console.log( e );
				}
				
				
				// validate
				if( !filters )
				{
					return false;
				}
				
				
				// filter only images
				$.each( filters.filters, function( k, v ){
				
					v.props.type = 'image';
					
				});
				
				
				// no need for 'uploaded' filter
				if( t.o.library == 'uploadedTo' )
				{
					filters.$el.find('option[value="uploaded"]').remove();
					filters.$el.after('<span>' + ba.l10n.image.uploadedTo + '</span>')
					
					$.each( filters.filters, function( k, v ){
						
						v.props.uploadedTo = ba.o.post_id;
						
					});
				}
				
				
				// remove non image options from filter list
				filters.$el.find('option').each(function(){
					
					// vars
					var v = $(this).attr('value');
					
					
					// don't remove the 'uploadedTo' if the library option is 'all'
					if( v == 'uploaded' && t.o.library == 'all' )
					{
						return;
					}
					
					if( v.indexOf('image') === -1 )
					{
						$(this).remove();
					}
					
				});
				
				
				// set default filter
				filters.$el.val('image').trigger('change');
				
			});
			
			
			// When an image is selected, run a callback.
			ba.media.frame.on( 'select', function() {
				
				// get selected images
				selection = _media.frame.state().get('selection');
				
				if( selection )
				{
					var i = 0;
					
					selection.each(function(attachment){
	
				    	// counter
				    	i++;
				    	
				    	
				    	// select / add another image field?
				    	if( i > 1 )
						{
							// vars
							var $td			=	_media.div.closest('td'),
								$tr 		=	$td.closest('.row'),
								$repeater 	=	$tr.closest('.repeater'),
								key 		=	$td.attr('data-field_key'),
								selector	=	'td .ba-image-uploader:first';
								
							
							// key only exists for repeater v1.0.1 +
							if( key )
							{
								selector = 'td[data-field_key="' + key + '"] .ba-image-uploader';
							}
							
							
							// add row?
							if( ! $tr.next('.row').exists() )
							{
								$repeater.find('.add-row-end').trigger('click');
								
							}
							
							
							// update current div
							_media.div = $tr.next('.row').find( selector );
							
						}
						
						
				    	// vars
				    	var image = {
					    	id		:	attachment.id,
					    	url		:	attachment.attributes.url
				    	};
				    	
				    	// is preview size available?
				    	if( attachment.attributes.sizes && attachment.attributes.sizes[ t.o.preview_size ] )
				    	{
					    	image.url = attachment.attributes.sizes[ t.o.preview_size ].url;
				    	}
				    	
				    	// add image to field
				        ba.fields.image.add( image );
				        
						
				    });
				    // selection.each(function(attachment){
				}
				// if( selection )
				
			});
			// ba.media.frame.on( 'select', function() {
					 
				
			// Finally, open the modal
			ba.media.frame.open();
				

			return false;
		},
		
		// temporary gallery fix		
		text : {
			title_add : "Select Image",
			title_edit : "Edit Image"
		}
		
	};
	
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('click', '.ba-image-uploader .ba-button-edit', function( e ){
		
		e.preventDefault();
		
		ba.fields.image.set({ $el : $(this).closest('.ba-image-uploader') }).edit();
			
	});
	
	$(document).on('click', '.ba-image-uploader .ba-button-delete', function( e ){
		
		e.preventDefault();
		
		ba.fields.image.set({ $el : $(this).closest('.ba-image-uploader') }).remove();
			
	});
	
	
	$(document).on('click', '.ba-image-uploader .add-image', function( e ){
		
		e.preventDefault();
		
		ba.fields.image.set({ $el : $(this).closest('.ba-image-uploader') }).popup();
		
	});
	

})(jQuery);

(function($){
	
	/*
	*  Radio
	*
	*  static model and events for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	ba.fields.radio = {
		
		$el : null,
		$input : null,
		$other : null,
		farbtastic : null,
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find input
			this.$input = this.$el.find('input[type="radio"]:checked');
			this.$other = this.$el.find('input[type="text"]');
			
			
			// return this for chaining
			return this;
			
		},
		change : function(){

			if( this.$input.val() == 'other' )
			{
				this.$other.attr('name', this.$input.attr('name'));
				this.$other.show();
			}
			else
			{
				this.$other.attr('name', '');
				this.$other.hide();
			}
		}
	};
	
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('change', '.ba-radio-list input[type="radio"]', function( e ){
		
		ba.fields.radio.set({ $el : $(this).closest('.ba-radio-list') }).change();
		
	});
	

})(jQuery);

(function($){
	
	/*
	*  Relationship
	*
	*  static model for this field
	*
	*  @type	event
	*  @date	1/06/13
	*
	*/
	
	ba.fields.relationship = {
		
		$el : null,
		$input : null,
		$left : null,
		$right : null,
				
		o : {},
		
		timeout : null,
		
		set : function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find elements
			this.$input = this.$el.children('input[type="hidden"]');
			this.$left = this.$el.find('.relationship_left'),
			this.$right = this.$el.find('.relationship_right');
			
			
			// get options
			this.o = ba.helpers.get_atts( this.$el );
			
			
			// return this for chaining
			return this;
			
		},
		init : function(){
			
			// reference
			var _this = this;
			
			
			// is clone field?
			if( ba.helpers.is_clone_field(this.$input) )
			{
				return;
			}
			
			
			// set height of right column
			this.$right.find('.relationship_list').height( this.$left.height() -2 );
			
			
			// right sortable
			this.$right.find('.relationship_list').sortable({
				axis					:	'y',
				items					:	'> li',
				forceHelperSize			:	true,
				forcePlaceholderSize	:	true,
				scroll					:	true,
				update					:	function(){
					
					_this.$input.trigger('change');
					
				}
			});
			
			
			// load more
			var $el = this.$el;
			
			this.$left.find('.relationship_list').scrollTop( 0 ).on('scroll', function(e){
				
				// validate
				if( $el.hasClass('loading') || $el.hasClass('no-results') )
				{
					return;
				}
				
				
				// Scrolled to bottom
				if( $(this).scrollTop() + $(this).innerHeight() >= $(this).get(0).scrollHeight )
				{
					var paged = parseInt( $el.attr('data-paged') );
					
					// update paged
					$el.attr('data-paged', (paged + 1) );
					
					// fetch
					_this.set({ $el : $el }).fetch();
				}
				
			});
			
			
			// ajax fetch values for left side
			this.fetch();
					
		},
		fetch : function(){
			
			// reference
			var _this = this,
				$el = this.$el;
			
			
			// add loading class, stops scroll loading
			$el.addClass('loading');
			
			
			// get results
		    $.ajax({
				url				:	ba.o.ajaxurl,
				type			:	'post',
				dataType		:	'json',
				data			:	$.extend({ 
					action		:	'ba/fields/relationship/query_posts', 
					post_id		:	ba.o.post_id,
					nonce		:	ba.o.nonce
				}, this.o ),
				success			:	function( json ){
					
					
					// render
					_this.set({ $el : $el }).render( json );
					
				}
			});
			
		},
		render : function( json ){
			
			// reference
			var _this = this;
			
			
			// update classes
			this.$el.removeClass('no-results').removeClass('loading');
			
			
			// new search?
			if( this.o.paged == 1 )
			{
				this.$el.find('.relationship_left li:not(.load-more)').remove();
			}
			
			
			// no results?
			if( ! json || ! json.html )
			{
				this.$el.addClass('no-results');
				return;
			}
			
			
			// append new results
			this.$el.find('.relationship_left .load-more').before( json.html );
			
			
			// next page?
			if( ! json.next_page_exists )
			{
				this.$el.addClass('no-results');
			}
							
			
			// apply .hide to left li's
			this.$left.find('a').each(function(){
				
				var id = $(this).attr('data-post_id');
				
				if( _this.$right.find('a[data-post_id="' + id + '"]').exists() )
				{
					$(this).parent().addClass('hide');
				}
				
			});
			
		},
		add : function( $a ){
			
			// vars
			var id = $a.attr('data-post_id'),
				title = $a.html();
			
			
			// max posts
			if( this.$right.find('a').length >= this.o.max )
			{
				alert( ba.l10n.relationship.max.replace('{max}', this.o.max) );
				return false;
			}
			
			
			// can be added?
			if( $a.parent().hasClass('hide') )
			{
				return false;
			}
			
			
			// hide
			$a.parent().addClass('hide');
			
			
			// template
			var html = [
				'<li>',
					'<a href="#" data-post_id="' + $a.attr('data-post_id') + '">',
						$a.html() + '<span class="ba-button-remove"></span>',
					'</a>',
					'<input type="hidden" name="' + this.$input.attr('name') + '[]" value="' + $a.attr('data-post_id') + '" />',
				'</li>'].join('');
			
	
			// add new li
			this.$right.find('.relationship_list').append( html )
			
			
			// trigger change on new_li
			this.$input.trigger('change');
			
			
			// validation
			this.$el.closest('.field').removeClass('error');

			
		},
		remove : function( $a ){
			
			// remove
			$a.parent().remove();
			
			
			// show
			this.$left.find('a[data-post_id="' + $a.attr('data-post_id') + '"]').parent('li').removeClass('hide');
			
			
			// trigger change on new_li
			this.$input.trigger('change');
			
		}
		
	};
	
	
	/*
	*  ba/setup_fields
	*
	*  run init function on all elements for this field
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/setup_fields', function(e, el){
		
		$(el).find('.ba_relationship').each(function(){
			
			ba.fields.relationship.set({ $el : $(this) }).init();
			
		});
		
	});
	
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('change', '.ba_relationship .select-post_type', function(e){
		
		// vars
		var val = $(this).val(),
			$el = $(this).closest('.ba_relationship');
			
		
		// update attr
	    $el.attr('data-post_type', val);
	    $el.attr('data-paged', 1);
	    
	    
	    // fetch
	    ba.fields.relationship.set({ $el : $el }).fetch();
		
	});

	
	$(document).on('click', '.ba_relationship .relationship_left .relationship_list a', function( e ){
		
		e.preventDefault();
		
		ba.fields.relationship.set({ $el : $(this).closest('.ba_relationship') }).add( $(this) );
		
		$(this).blur();
		
	});
	
	$(document).on('click', '.ba_relationship .relationship_right .relationship_list a', function( e ){
		
		e.preventDefault();
		
		ba.fields.relationship.set({ $el : $(this).closest('.ba_relationship') }).remove( $(this) );
		
		$(this).blur();
		
	});
	
	$(document).on('keyup', '.ba_relationship input.relationship_search', function( e ){
		
		// vars
		var val = $(this).val(),
			$el = $(this).closest('.ba_relationship');
			
		
		// update attr
	    $el.attr('data-s', val);
	    $el.attr('data-paged', 1);
	    
	    
	    // fetch
	    clearTimeout( ba.fields.relationship.timeout );
	    ba.fields.relationship.timeout = setTimeout(function(){
	    
	    	 ba.fields.relationship.set({ $el : $el }).fetch();
	    	
	    }, 500);
		
	});
	
	$(document).on('keypress', '.ba_relationship input.relationship_search', function( e ){
		
		// don't submit form
		if( e.which == 13 )
		{
			e.preventDefault();
		}
		
	});
	

})(jQuery);

(function($){

	ba.fields.tab = {
		
		add_group : function( $wrap ){
			
			// vars
			var html = '';
			
			
			// generate html
			if( $wrap.is('tbody') )
			{
				html = '<tr class="ba-tab-wrap"><td colspan="2"><ul class="hl clearfix ba-tab-group"></ul></td></tr>';
			}
			else
			{
				html = '<div class="ba-tab-wrap"><ul class="hl clearfix ba-tab-group"></ul></div>';
			}
			
			
			// append html
			$wrap.children('.field_type-tab:first').before( html );
			
		},
		
		add_tab : function( $tab ){
			
			// vars
			var $field	= $tab.closest('.field'),
				$wrap	= $field.parent(),
				
				key		= $field.attr('data-field_key'),
				label 	= $tab.text();
				
				
			// create tab group if it doesnt exist
			if( ! $wrap.children('.ba-tab-wrap').exists() )
			{
				this.add_group( $wrap );
			}
			
			// add tab
			$wrap.children('.ba-tab-wrap').find('.ba-tab-group').append('<li><a class="ba-tab-button" href="#" data-key="' + key + '">' + label + '</a></li>');
			
		},
		
		toggle : function( $a ){
			
			// reference
			var _this = this;
				
				
			//console.log( 'toggle %o ', $a);
			// vars
			var $wrap	= $a.closest('.ba-tab-wrap').parent(),
				key		= $a.attr('data-key');
			
			
			// classes
			$a.parent('li').addClass('active').siblings('li').removeClass('active');
			
			
			// hide / show
			$wrap.children('.field_type-tab').each(function(){
			
				
				// vars
				var $tab = $(this);
					
				
				if( $tab.attr('data-field_key') == key  )
				{
					_this.show_tab_fields( $(this) );
				}
				else
				{
					_this.hide_tab_fields( $(this) );
				}
				
				
			});
			
		},
		
		show_tab_fields : function( $field ) {
			
			//console.log('show tab fields %o', $field);
			$field.nextUntil('.field_type-tab').each(function(){
				
				$(this).removeClass('ba-tab_group-hide').addClass('ba-tab_group-show');
				$(document).trigger('ba/fields/tab/show', [ $(this) ]);
				
			});
		},
		
		hide_tab_fields : function( $field ) {
			
			$field.nextUntil('.field_type-tab').each(function(){
				
				$(this).removeClass('ba-tab_group-show').addClass('ba-tab_group-hide');
				$(document).trigger('ba/fields/tab/hide', [ $(this) ]);
				
			});
		},
		
		refresh : function( $el ){
			
			// reference
			var _this = this;
			
			
			// trigger
			$el.find('.ba-tab-group').each(function(){
				
				$(this).find('.ba-tab-button:first').each(function(){
					
					_this.toggle( $(this) );
					
				});
				
			});

		}
		
	};
	
	
	/*
	*  ba/setup_fields
	*
	*  run init function on all elements for this field
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/setup_fields', function(e, el){
		
		// add tabs
		$(el).find('.ba-tab').each(function(){
			
			ba.fields.tab.add_tab( $(this) );
			
		});
		
		
		// activate first tab
		ba.fields.tab.refresh( $(el) );
		
		
		// NOTE: this code is defined BEFORE the ba.conditional_logic action. This is becuase the 'ba/setup_fields' listener is defined INSIDE the conditional_logic.init() function which is run on doc.ready
		
		// trigger conditional logic
		// this code ( ba/setup_fields ) is run after the main ba.conditional_logic.init();
		//console.log('ba/setup_fields (after tab refresh) calling ba.conditional_logic.refresh()');
		//ba.conditional_logic.refresh();
		
	});
	
	
		
	
	/*
	*  Events
	*
	*  jQuery events for this field
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('click', '.ba-tab-button', function( e ){
		
		e.preventDefault();
		
		ba.fields.tab.toggle( $(this) );
		
		$(this).trigger('blur');
		
	});
	
	
	$(document).on('ba/conditional_logic/hide', function( e, $target, item ){
		
		// validate
		if( $target.attr('data-field_type') != 'tab' )
		{
			return;
		}
		
		//console.log('conditional_logic/hide tab %o', $target);
		
		
		// vars
		var $tab = $target.siblings('.ba-tab-wrap').find('a[data-key="' + $target.attr('data-field_key') + '"]');
		
		
		// if tab is already hidden, then ignore the following functiolnality
		if( $tab.is(':hidden') )
		{
			return;
		}
		
		
		// visibility
		$tab.parent().hide();
		
		
		// if 
		if( $tab.parent().siblings(':visible').exists() )
		{
			// if the $target to be hidden is a tab button, lets toggle a sibling tab button
			$tab.parent().siblings(':visible').first().children('a').trigger('click');
		}
		else
		{
			// no onther tabs
			ba.fields.tab.hide_tab_fields( $target );
		}
		
	});
	
	
	$(document).on('ba/conditional_logic/show', function( e, $target, item ){
		
		// validate
		if( $target.attr('data-field_type') != 'tab' )
		{
			return;
		}
		
		
		//console.log('conditional_logic/show tab %o', $target);
		
		
		// vars
		var $tab = $target.siblings('.ba-tab-wrap').find('a[data-key="' + $target.attr('data-field_key') + '"]');
		
		
		// if tab is already visible, then ignore the following functiolnality
		if( $tab.is(':visible') )
		{
			return;
		}
		
		
		// visibility
		$tab.parent().show();
		
		
		// if this is the active tab
		if( $tab.parent().hasClass('active') )
		{
			$tab.trigger('click');
			return;
		}
		
		
		// if the sibling active tab is actually hidden by conditional logic, take ownership of tabs
		if( $tab.parent().siblings('.active').is(':hidden') )
		{
			// show this tab group
			$tab.trigger('click');
			return;
		}
		

	});
	
	

})(jQuery);

(function($){
	
	
	/*
	*  Validation
	*
	*  JS model
	*
	*  @type	object 
	*  @date	1/06/13
	*
	*/
	
	ba.validation = {
	
		status		: true,
		disabled	: false,
		
		run : function(){
			
			// reference
			var _this = this;
			
			
			// reset
			_this.status = true;
			
			
			// loop through all fields
			$('.field.required, .form-field.required').each(function(){
				
				// run validation
				_this.validate( $(this) );
				
	
			});
			// end loop through all fields
		},
		
		/*
		*  show_spinner
		*
		*  This function will show a spinner element. Logic changed in WP 4.2
		*
		*  @type	function
		*  @date	3/05/2015
		*  @since	5.2.3
		*
		*  @param	$spinner (jQuery)
		*  @return	n/a
		*/
		
		show_spinner: function( $spinner ){
			
			// bail early if no spinner
			if( !$spinner.exists() ) {
				
				return;
				
			}
			
			
			// vars
			var wp_version = ba.o.wp_version;
			
			
			// show
			if( parseFloat(wp_version) >= 4.2 ) {
				
				$spinner.addClass('is-active');
			
			} else {
				
				$spinner.css('display', 'inline-block');
			
			}
			
		},
		
		
		/*
		*  hide_spinner
		*
		*  This function will hide a spinner element. Logic changed in WP 4.2
		*
		*  @type	function
		*  @date	3/05/2015
		*  @since	5.2.3
		*
		*  @param	$spinner (jQuery)
		*  @return	n/a
		*/
		
		hide_spinner: function( $spinner ){
			
			// bail early if no spinner
			if( !$spinner.exists() ) {
				
				return;
				
			}
			
			
			// vars
			var wp_version = ba.o.wp_version;
			
			
			// hide
			if( parseFloat(wp_version) >= 4.2 ) {
				
				$spinner.removeClass('is-active');
			
			} else {
				
				$spinner.css('display', 'none');
			
			}
			
		},
		
		validate : function( div ){
			
			// var
			var ignore = false,
				$tab = null;
			
			
			// set validation data
			div.data('validation', true);
			
			
			// not visible
			if( div.is(':hidden') )
			{
				// ignore validation
				ignore = true;
				
				
				// if this field is hidden by a tab group, allow validation
				if( div.hasClass('ba-tab_group-hide') )
				{
					ignore = false;
					
					
					// vars
					var $tab_field = div.prevAll('.field_type-tab:first'),
						$tab_group = div.prevAll('.ba-tab-wrap:first');
					
					
					// if the tab itself is hidden, bypass validation
					if( $tab_field.hasClass('ba-conditional_logic-hide') )
					{
						ignore = true;
					}
					else
					{
						// activate this tab as it holds hidden required field!
						$tab = $tab_group.find('.ba-tab-button[data-key="' + $tab_field.attr('data-field_key') + '"]');
					}
				}
			}
			
			
			// if is hidden by conditional logic, ignore
			if( div.hasClass('ba-conditional_logic-hide') )
			{
				ignore = true;
			}
			
			
			// if field group is hidden, igrnoe
			if( div.closest('.postbox.ba-hidden').exists() ) {
				
				ignore = true;
				
			}
			
			
			if( ignore )
			{
				return;
			}
			
			
			
			// text / textarea
			if( div.find('input[type="text"], input[type="email"], input[type="number"], input[type="hidden"], textarea').val() == "" )
			{
				div.data('validation', false);
			}
			
			
			// wysiwyg
			if( div.find('.ba_wysiwyg').exists() && typeof(tinyMCE) == "object")
			{
				div.data('validation', true);
				
				var id = div.find('.wp-editor-area').attr('id'),
					editor = tinyMCE.get( id );


				if( editor && !editor.getContent() )
				{
					div.data('validation', false);
				}
			}
			
			
			// select
			if( div.find('select').exists() )
			{
				div.data('validation', true);

				if( div.find('select').val() == "null" || ! div.find('select').val() )
				{
					div.data('validation', false);
				}
			}

			
			// radio
			if( div.find('input[type="radio"]').exists() )
			{
				div.data('validation', false);

				if( div.find('input[type="radio"]:checked').exists() )
				{
					div.data('validation', true);
				}
			}
			
			
			// checkbox
			if( div.find('input[type="checkbox"]').exists() )
			{
				div.data('validation', false);

				if( div.find('input[type="checkbox"]:checked').exists() )
				{
					div.data('validation', true);
				}
			}

			
			// relationship
			if( div.find('.ba_relationship').exists() )
			{
				div.data('validation', false);
				
				if( div.find('.ba_relationship .relationship_right input').exists() )
				{
					div.data('validation', true);
				}
			}
			
			
			// repeater
			if( div.find('.repeater').exists() )
			{
				div.data('validation', false);
				
				if( div.find('.repeater tr.row').exists() )
				{
					div.data('validation', true);
				}			
			}
			
			
			// gallery
			if( div.find('.ba-gallery').exists() )
			{
				div.data('validation', false);
				
				if( div.find('.ba-gallery .thumbnail').exists())
				{
					div.data('validation', true);
				}
			}
			
			
			// hook for custom validation
			$(document).trigger('ba/validate_field', [ div ] );
			
			
			// set validation
			if( ! div.data('validation') )
			{
				// show error
				this.status = false;
				div.closest('.field').addClass('error');
				
				
				// custom validation message
				if( div.data('validation_message') )
				{
					var $label = div.find('p.label:first'),
						$message = null;
						
					
					// remove old message
					$label.children('.ba-error-message').remove();
					
					
					$label.append( '<span class="ba-error-message"><i class="bit"></i>' + div.data('validation_message') + '</span>' );
				}
				
				
				// display field (curently hidden due to another tab being active)
				if( $tab )
				{
					$tab.trigger('click');
				}
				
			}
		}
		
	};
	
	
	/*
	*  Events
	*
	*  Remove error class on focus
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('focus click', '.field.required input, .field.required textarea, .field.required select', function( e ){
	
		$(this).closest('.field').removeClass('error');
		
	});
	
	
	/*
	$(document).on('blur change', '.field.required input, .field.required textarea, .field.required select', function( e ){
		
			ba.validation.validate( $(this).closest('.field') );
			
		});
	*/
	
	
	/*
	*  Save Post
	*
	*  If user is saving a draft, allow them to bypass the validation
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('click', '#save-post', function(){
		
		ba.validation.disabled = true;
		
	});
	
	
	/*
	*  Submit Post
	*
	*  Run validation and return true|false accordingly
	*
	*  @type	function
	*  @date	1/03/2011
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	$(document).on('submit', '#post', function(){
		
		// If disabled, bail early on the validation check
		if( ba.validation.disabled )
		{
			return true;
		}
		
		
		// do validation
		ba.validation.run();
			
			
		if( ! ba.validation.status ) {
			
			// vars
			var $form = $(this);
			
			
			// show message
			$form.siblings('#message').remove();
			$form.before('<div id="message" class="error"><p>' + ba.l10n.validation.error + '</p></div>');
			
			
			// hide ajax stuff on submit button
			if( $('#submitdiv').exists() ) {
				
				// remove disabled classes
				$('#submitdiv').find('.disabled').removeClass('disabled');
				$('#submitdiv').find('.button-disabled').removeClass('button-disabled');
				$('#submitdiv').find('.button-primary-disabled').removeClass('button-primary-disabled');
				
				
				// remove spinner
				ba.validation.hide_spinner( $('#submitdiv .spinner') );
				
			}
			
			return false;
		}

		
		// remove hidden postboxes
		// + this will stop them from being posted to save
		$('.ba_postbox.ba-hidden').remove();
		

		// submit the form
		return true;
		
	});
	

})(jQuery);

(function($){
	
	/*
	*  WYSIWYG
	*
	*  jQuery functionality for this field type
	*
	*  @type	object
	*  @date	20/07/13
	*
	*  @param	N/A
	*  @return	N/A
	*/
	
	var _wysiwyg = ba.fields.wysiwyg = {
		
		$el: null,
		$textarea: null,
		
		o: {},
		
		set: function( o ){
			
			// merge in new option
			$.extend( this, o );
			
			
			// find textarea
			this.$textarea = this.$el.find('textarea');
			
			
			// get options
			this.o = ba.helpers.get_atts( this.$el );
			this.o.id = this.$textarea.attr('id');
			
			
			// return this for chaining
			return this;
			
		},
		
		has_tinymce : function(){
		
			var r = false;
			
			if( typeof(tinyMCE) == "object" )
			{
				r = true;
			}
			
			return r;
			
		},
		
		get_toolbar : function(){
			
			// safely get toolbar
			if( ba.helpers.isset( this, 'toolbars', this.o.toolbar ) ) {
				
				return this.toolbars[ this.o.toolbar ];
				
			}
			
			
			// return
			return false;
			
		},
		
		init : function(){
			
			// is clone field?
			if( ba.helpers.is_clone_field( this.$textarea ) )
			{
				return;
			}
			
			
			// vars
			var id = this.o.id,
				toolbar = this.get_toolbar(),
				command = 'mceAddControl',
				setting = 'theme_advanced_buttons{i}';
			
			
			// backup
			var _settings = $.extend( {}, tinyMCE.settings );
			
			
			// v4 settings
			if( tinymce.majorVersion == 4 ) {
				
				command = 'mceAddEditor';
				setting = 'toolbar{i}';
				
			}
			
			
			// add toolbars
			if( toolbar ) {
					
				for( var i = 1; i < 5; i++ ) {
					
					// vars
					var v = '';
					
					
					// load toolbar
					if( ba.helpers.isset( toolbar, 'theme_advanced_buttons' + i ) ) {
						
						v = toolbar['theme_advanced_buttons' + i];
						
					}
					
					
					// update setting
					tinyMCE.settings[ setting.replace('{i}', i) ] = v;
					
				}
				
			}
			
			
			// add editor
			tinyMCE.execCommand( command, false, id);
			
			
			// events - load
			$(document).trigger('ba/wysiwyg/load', id);
			
			
			// add events (click, focus, blur) for inserting image into correct editor
			setTimeout(function(){
				
				_wysiwyg.add_events( id );
				
			}, 100);
				
			
			// restore tinyMCE.settings
			tinyMCE.settings = _settings;
			
			
			// set active editor to null
			wpActiveEditor = null;
					
		},
		
		add_events: function( id ){
			
			// vars
			var editor = tinyMCE.get( id );
			
			
			// validate
			if( !editor ) return;
			
			
			// vars
			var	$container = $('#wp-' + id + '-wrap'),
				$body = $( editor.getBody() );
	
			
			// events
			$container.on('click', function(){
			
				$(document).trigger('ba/wysiwyg/click', id);
				
			});
			
			$body.on('focus', function(){
			
				$(document).trigger('ba/wysiwyg/focus', id);
				
			});
			
			$body.on('blur', function(){
			
				$(document).trigger('ba/wysiwyg/blur', id);
				
			});
			
			
		},
		destroy : function(){
			
			// vars
			var id = this.o.id,
				command = 'mceRemoveControl';
			
			
			// Remove tinymcy functionality.
			// Due to the media popup destroying and creating the field within such a short amount of time,
			// a JS error will be thrown when launching the edit window twice in a row.
			try {
				
				// vars
				var editor = tinyMCE.get( id );
				
				
				// validate
				if( !editor ) {
					
					return;
					
				}
				
				
				// v4 settings
				if( tinymce.majorVersion == 4 ) {
					
					command = 'mceRemoveEditor';
					
				}
				
				
				// store value
				var val = editor.getContent();
				
				
				// remove editor
				tinyMCE.execCommand(command, false, id);
				
				
				// set value
				this.$textarea.val( val );
				
				
			} catch(e) {
				
				//console.log( e );
				
			}
			
			
			// set active editor to null
			wpActiveEditor = null;
			
		}
		
	};
	
	
	/*
	*  ba/setup_fields
	*
	*  run init function on all elements for this field
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/setup_fields', function(e, el){
		
		// validate
		if( ! _wysiwyg.has_tinymce() )
		{
			return;
		}
		
		
		// Destory all WYSIWYG fields
		// This hack will fix a problem when the WP popup is created and hidden, then the ACF popup (image/file field) is opened
		$(el).find('.ba_wysiwyg').each(function(){
			
			_wysiwyg.set({ $el : $(this) }).destroy();
			
		});
		
		
		// Add WYSIWYG fields
		setTimeout(function(){
			
			$(el).find('.ba_wysiwyg').each(function(){
			
				_wysiwyg.set({ $el : $(this) }).init();
				
			});
			
		}, 0);
		
	});
	
	
	/*
	*  ba/remove_fields
	*
	*  This action is called when the $el is being removed from the DOM
	*
	*  @type	event
	*  @date	20/07/13
	*
	*  @param	{object}	e		event object
	*  @param	{object}	$el		jQuery element being removed
	*  @return	N/A
	*/
	
	$(document).on('ba/remove_fields', function(e, $el){
		
		// validate
		if( ! _wysiwyg.has_tinymce() )
		{
			return;
		}
		
		
		$el.find('.ba_wysiwyg').each(function(){
			
			_wysiwyg.set({ $el : $(this) }).destroy();
			
		});
		
	});
		
	
	/*
	*  ba/wysiwyg/click
	*
	*  this event is run when a user clicks on a WYSIWYG field
	*
	*  @type	event
	*  @date	17/01/13
	*
	*  @param	{object}	e		event object
	*  @param	{int}		id		WYSIWYG ID
	*  @return	N/A
	*/
	
	$(document).on('ba/wysiwyg/click', function(e, id){
		
		wpActiveEditor = id;
		
		container = $('#wp-' + id + '-wrap').closest('.field').removeClass('error');
		
	});
	
	
	/*
	*  ba/wysiwyg/focus
	*
	*  this event is run when a user focuses on a WYSIWYG field body
	*
	*  @type	event
	*  @date	17/01/13
	*
	*  @param	{object}	e		event object
	*  @param	{int}		id		WYSIWYG ID
	*  @return	N/A
	*/
	
	$(document).on('ba/wysiwyg/focus', function(e, id){
		
		wpActiveEditor = id;
		
		container = $('#wp-' + id + '-wrap').closest('.field').removeClass('error');
		
	});
	
	
	/*
	*  ba/wysiwyg/blur
	*
	*  this event is run when a user loses focus on a WYSIWYG field body
	*
	*  @type	event
	*  @date	17/01/13
	*
	*  @param	{object}	e		event object
	*  @param	{int}		id		WYSIWYG ID
	*  @return	N/A
	*/
	
	$(document).on('ba/wysiwyg/blur', function(e, id){
		
		wpActiveEditor = null;
		
		// update the hidden textarea
		// - This fixes a but when adding a taxonomy term as the form is not posted and the hidden tetarea is never populated!
		var editor = tinyMCE.get( id );
		
		
		// validate
		if( !editor )
		{
			return;
		}
		
		
		var el = editor.getElement();
		
			
		// save to textarea	
		editor.save();
		
		
		// trigger change on textarea
		$( el ).trigger('change');
		
	});

	
	/*
	*  ba/sortable_start
	*
	*  this event is run when a element is being drag / dropped
	*
	*  @type	event
	*  @date	10/11/12
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/sortable_start', function(e, el) {
		
		// validate
		if( ! _wysiwyg.has_tinymce() )
		{
			return;
		}
		
		
		$(el).find('.ba_wysiwyg').each(function(){
			
			_wysiwyg.set({ $el : $(this) }).destroy();
			
		});
		
	});
	
	
	/*
	*  ba/sortable_stop
	*
	*  this event is run when a element has finnished being drag / dropped
	*
	*  @type	event
	*  @date	10/11/12
	*
	*  @param	{object}	e		event object
	*  @param	{object}	el		DOM object which may contain new ACF elements
	*  @return	N/A
	*/
	
	$(document).on('ba/sortable_stop', function(e, el) {
		
		// validate
		if( ! _wysiwyg.has_tinymce() )
		{
			return;
		}
		
		
		$(el).find('.ba_wysiwyg').each(function(){
			
			_wysiwyg.set({ $el : $(this) }).init();
			
		});
		
	});
	
	
	/*
	*  window load
	*
	*  @description: 
	*  @since: 3.5.5
	*  @created: 22/12/12
	*/
	
	$(window).on('load', function(){
		
		// validate
		if( ! _wysiwyg.has_tinymce() )
		{
			return;
		}
		
		
		// vars
		var wp_content = $('#wp-content-wrap').exists(),
			wp_ba_settings = $('#wp-ba_settings-wrap').exists()
			mode = 'tmce';
		
		
		// has_editor
		if( wp_ba_settings )
		{
			// html_mode
			if( $('#wp-ba_settings-wrap').hasClass('html-active') )
			{
				mode = 'html';
			}
		}
		
		
		setTimeout(function(){
			
			// trigger click on hidden wysiwyg (to get in HTML mode)
			if( wp_ba_settings && mode == 'html' )
			{
				$('#ba_settings-tmce').trigger('click');
			}
			
		}, 1);
		
		
		setTimeout(function(){
			
			// trigger html mode for people who want to stay in HTML mode
			if( wp_ba_settings && mode == 'html' )
			{
				$('#ba_settings-html').trigger('click');
			}
			
			// Add events to content editor
			if( wp_content )
			{
				_wysiwyg.add_events('content');
			}
			
			
		}, 11);
		
		
	});
	
	
	/*
	*  Full screen
	*
	*  @description: this hack will hide the 'image upload' button in the wysiwyg full screen mode if the field has disabled image uploads!
	*  @since: 3.6
	*  @created: 26/02/13
	*/
	
	$(document).on('click', '.ba_wysiwyg a.mce_fullscreen', function(){
		
		// vars
		var wysiwyg = $(this).closest('.ba_wysiwyg'),
			upload = wysiwyg.attr('data-upload');
		
		if( upload == 'no' )
		{
			$('#mce_fullscreen_container td.mceToolbar .mce_add_media').remove();
		}
		
	});
	
	
})(jQuery);

