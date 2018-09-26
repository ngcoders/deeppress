<?php

class dp_field_text extends dp_field
{

	/*
	*  __construct
	*
	*  Set name / label needed for actions / filters
	*
	*  @since	3.6
	*  @date	23/01/13
	*/

	function __construct()
	{
		// vars
		$this->name = 'text';
		$this->label = __("Text",'ba');
		$this->defaults = array(
			'default_value'	=>	'',
			'formatting' 	=>	'html',
			'maxlength'		=>	'',
			'placeholder'	=>	'',
			'prepend'		=>	'',
			'append'		=>	''
		);


		// do not delete!
		parent::__construct();
	}



	/*
	*  create_field()
	*
	*  Create the HTML interface for your field
	*
	*  @param	$field - an array holding all the field's data
	*
	*  @type	action
	*  @since	3.6
	*  @date	23/01/13
	*/

	function create_field( $field )
	{
		// vars
		$o = array( 'id', 'class', 'name', 'value', 'placeholder' );
		$e = '';


		// maxlength
		if( $field['maxlength'] !== "" )
		{
			$o[] = 'maxlength';
		}


		// prepend
		if( $field['prepend'] !== "" )
		{
			$field['class'] .= ' ba-is-prepended';
			$e .= '<div class="ba-input-prepend">' . $field['prepend'] . '</div>';
		}


		// append
		if( $field['append'] !== "" )
		{
			$field['class'] .= ' ba-is-appended';
			$e .= '<div class="ba-input-append">' . $field['append'] . '</div>';
		}


		$e .= '<div class="ba-input-wrap">';
		$e .= '<input type="text"';

		foreach( $o as $k )
		{
			$e .= ' ' . $k . '="' . esc_attr( $field[ $k ] ) . '"';
		}

		$e .= ' />';
		$e .= '</div>';


		// return
		echo $e;
	}


	/*
	*  create_options()
	*
	*  Create extra options for your field. This is rendered when editing a field.
	*  The value of $field['name'] can be used (like bellow) to save extra data to the $field
	*
	*  @param	$field	- an array holding all the field's data
	*
	*  @type	action
	*  @since	3.6
	*  @date	23/01/13
	*/

	function create_options( $field )
	{
		// vars
		$key = $field['name'];

		?>
		<tr class="field_option field_option_<?php echo $this->name; ?>">
			<td class="label">
				<label><?php _e("Default Value",'ba'); ?></label>
				<p><?php _e("Appears when creating a new post",'ba') ?></p>
			</td>
			<td>
				<?php
				do_action('dp/create_field', array(
					'type'	=>	'text',
					'name'	=>	'fields[' .$key.'][default_value]',
					'value'	=>	$field['default_value'],
				));
				?>
			</td>
		</tr>
		<tr class="field_option field_option_<?php echo $this->name; ?>">
			<td class="label">
				<label><?php _e("Placeholder Text",'ba'); ?></label>
				<p><?php _e("Appears within the input",'ba') ?></p>
			</td>
			<td>
				<?php
				do_action('dp/create_field', array(
					'type'	=>	'text',
					'name'	=>	'fields[' .$key.'][placeholder]',
					'value'	=>	$field['placeholder'],
				));
				?>
			</td>
		</tr>
		<tr class="field_option field_option_<?php echo $this->name; ?>">
			<td class="label">
				<label><?php _e("Prepend",'ba'); ?></label>
				<p><?php _e("Appears before the input",'ba') ?></p>
			</td>
			<td>
				<?php
				do_action('dp/create_field', array(
					'type'	=>	'text',
					'name'	=>	'fields[' .$key.'][prepend]',
					'value'	=>	$field['prepend'],
				));
				?>
			</td>
		</tr>
		<tr class="field_option field_option_<?php echo $this->name; ?>">
			<td class="label">
				<label><?php _e("Append",'ba'); ?></label>
				<p><?php _e("Appears after the input",'ba') ?></p>
			</td>
			<td>
				<?php
				do_action('dp/create_field', array(
					'type'	=>	'text',
					'name'	=>	'fields[' .$key.'][append]',
					'value'	=>	$field['append'],
				));
				?>
			</td>
		</tr>
		<tr class="field_option field_option_<?php echo $this->name; ?>">
			<td class="label">
				<label><?php _e("Formatting",'ba'); ?></label>
				<p><?php _e("Affects value on front end",'ba') ?></p>
			</td>
			<td>
				<?php
				do_action('dp/create_field', array(
					'type'	=>	'select',
					'name'	=>	'fields['.$key.'][formatting]',
					'value'	=>	$field['formatting'],
					'choices' => array(
						'none'	=>	__("No formatting",'ba'),
						'html'	=>	__("Convert HTML into tags",'ba')
					)
				));
				?>
			</td>
		</tr>
		<tr class="field_option field_option_<?php echo $this->name; ?>">
			<td class="label">
				<label><?php _e("Character Limit",'ba'); ?></label>
				<p><?php _e("Leave blank for no limit",'ba') ?></p>
			</td>
			<td>
				<?php
				do_action('dp/create_field', array(
					'type'	=>	'number',
					'name'	=>	'fields[' .$key.'][maxlength]',
					'value'	=>	$field['maxlength'],
				));
				?>
			</td>
		</tr>
		<?php

	}


	/*
	*  format_value()
	*
	*  This filter is appied to the $value after it is loaded from the db and before it is passed to the create_field action
	*
	*  @type	filter
	*  @since	3.6
	*  @date	23/01/13
	*
	*  @param	$value	- the value which was loaded from the database
	*  @param	$post_id - the $post_id from which the value was loaded
	*  @param	$field	- the field array holding all the field options
	*
	*  @return	$value	- the modified value
	*/

	function format_value( $value, $post_id, $field )
	{
		$value = htmlspecialchars($value, ENT_QUOTES);

		return $value;
	}


	/*
	*  format_value_for_api()
	*
	*  This filter is appied to the $value after it is loaded from the db and before it is passed back to the api functions such as the_field
	*
	*  @type	filter
	*  @since	3.6
	*  @date	23/01/13
	*
	*  @param	$value	- the value which was loaded from the database
	*  @param	$post_id - the $post_id from which the value was loaded
	*  @param	$field	- the field array holding all the field options
	*
	*  @return	$value	- the modified value
	*/

	function format_value_for_api( $value, $post_id, $field )
	{
		// validate type
		if( !is_string($value) )
		{
			return $value;
		}


		if( $field['formatting'] == 'none' )
		{
			$value = htmlspecialchars($value, ENT_QUOTES);
		}
		elseif( $field['formatting'] == 'html' )
		{
			$value = nl2br($value);
		}


		return $value;
	}

}

new dp_field_text();

?>