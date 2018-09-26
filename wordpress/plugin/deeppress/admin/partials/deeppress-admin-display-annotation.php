<?php ?>
<div class="wrap">

	<h1 class="wp-heading-inline">Annotate</h1>
	<a href="<?php echo $_SERVER['HTTP_REFERER'] ?>" class="page-title-action">Back</a>
	<div>
		<div>
			<button id="save-annotation" class="save-button button" data-action="save">Save</button>
			<button id="save-annotation-next" class="save-button button" data-action="save-next">Save & Next</button>
			<button id="skip" class="save-button button" data-action="skip">Skip</button>
			<span id="result"></span>
		</div>
		<div class="annotatable-image-box">
			<img src="<?php echo $record['image']; ?>" id="annotatable">
		</div>
		<div id="result"></div>
		<input type="hidden" id="record-id" value="<?php echo $record['id']; ?>">
	</div>

	<button id="delete" class="save-button button" data-action="delete">Delete</button>
	<div>
		<table>
			<tr>
				<td>Added On</td><td id="col-created-at"><?php echo $record['created_at']; ?></td>
			</tr>
			<tr>
				<td>Processed</td><td id="col-processed"><?php echo $record['processed']; ?></td>
			</tr>
		</table>
	</div>
</div>
<script type="text/javascript" >
    jQuery(document).ready(function($) {
        var saveAnnotation = function(e){
            console.log(e);
            $(".save-button").prop("disabled", true);
            var areas = $('img#annotatable').selectAreas('areas');
            console.log(areas);
            $("#result").html("");
            var data = {
                action: 'deeppress_save_annotation',
                id: $("#record-id").val(),
                box: areas,
                sub_action: $(e.target).data("action")
            };
            jQuery.post(ajaxurl, data, function(response) {
                var resData = response.data;
                $('#result').html(resData);
                var next = response.next;
                var nextId = response.next.id;
                if (!nextId)
                    return;
                var nextImageUrl = next.image;
                $("#record-id").val(nextId);
                $("#annotatable").attr("src",nextImageUrl);
                $('img#annotatable').selectAreas('reset');

                $("#col-processed").html(next.processed);
                $("#col-created-at").html(next.created_at);

                setTimeout(function() {
                    $(".save-button").prop("disabled", false);
                    $('#result').html("");
                }, 1500);

                try {
                    var jsonStr = next.detections;
                    if(next.annotated == '1') {
                        jsonStr = next.box;
                    }
                    var detections = JSON.parse(jsonStr);
                    for(var i = 0; i < detections.length; i++){
                        var box = detections[i];
                        console.log(box);
                        $('img#annotatable').selectAreas('add', box);
                    }
                } catch(e) {
                    console.log(e); // error in the above string (in this case, yes)!
                }

            });
        };
        $(".save-button").click(saveAnnotation);
        $('img#annotatable').selectAreas({
            overlayOpacity: 0.1,
            areas: [<?php echo $box_str; ?>],
            objectClassList: <?php echo $classes; ?>
        });
    });
</script>
