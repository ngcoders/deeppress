<?php ?>
<div class="wrap">

	<h1 class="wp-heading-inline">Test</h1>
	<div>
        <table>
            <tr>
                <td>
                Action: <select name="type" id="action-type">
                        <option value="detection">Object detection</option>
                        <option value="classification">Classification</option>
                    </select>
                </td>
                <td>
                    Model: <select name="model" id="model">
                        
                    </select>
                </td>
                <td>
                    <input type="file" id="imgfile">
                </td>
                <td>
                <button id="test-button" class="test-button button">Test</button>
                </td>
            </tr>
        </table>
        
	</div>

	
	<div>
    <canvas id="canvas"></canvas>
	</div>
    <div>
    <p>Response</p>
    <div id="response" style="
        display: block;
        white-space: pre;
        font-family: monospace;
        background: #fff;
        border-radius: 5px;
        padding: 10px;
    ">
    
    </div>
    </div>
</div>
<script type="text/javascript" >
var img, input, file;
    

    jQuery(document).ready(function($) {
        function get_models(){
            var data = {
                action: 'dp_get_models',
                type: $("#action-type").val()
            }
            jQuery.post(ajaxurl, data, function(response) {
                    var models = response.data;
                    $("#model").html("");
                    for(var i = 0; i < models.length; i++){
                        $("#model").append('<option values="' + models[i].file_name + '">' + models[i].name + '</option>');
                    }                
            });
        }
        $("#action-type").change(function(){
            get_models();
        })
        get_models();
        $("#test-button").click(function(){
            loadImage();
            
        
        });

        function loadImage() {
        var input, fr;

        if (typeof window.FileReader !== 'function') {
            write("The file API isn't supported on this browser yet.");
            return;
        }

        input = document.getElementById('imgfile');
        if (!input) {
            write("Um, couldn't find the imgfile element.");
        }
        else if (!input.files) {
            write("This browser doesn't seem to support the `files` property of file inputs.");
        }
        else if (!input.files[0]) {
            write("Please select a file before clicking 'Load'");
        }
        else {
            file = input.files[0];
            fr = new FileReader();
            fr.onload = createImage;
            fr.readAsDataURL(file);
        }

        function createImage() {
            img = new Image();
            img.onload = imageLoaded;
            img.src = fr.result;
        }

        

        function write(msg) {
            var p = document.createElement('p');
            p.innerHTML = msg;
            document.body.appendChild(p);
        }
    }
    function imageLoaded() {
        var canvas = document.getElementById("canvas")
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img,0,0);
        // alert(canvas.toDataURL("image/png"));
        
        var fd = new FormData();
        fd.append("image", file);
        fd.append("model", $("#model").val());
        fd.append("thresh", 0.25);
        $.ajax({
            url:"http://localhost:8080/detect", 
            data:fd,
            type: 'POST',
            processData: false,
            contentType: false,
            success: function(data){
                console.log(data);
                $("#response").html(JSON.stringify(data, null, 2));
                if(data.success){
                    var box = data.box;
                    var canvas = document.getElementById("canvas")
                    var ctx = canvas.getContext("2d");
                    for(var i = 0; i < box.length; i++){
                        ctx.beginPath();
                        var x= box[i].x, y = box[i].y; 
                        ctx.rect(x, y, box[i].width, box[i].height);
                        ctx.lineWidth = 2;
                        ctx.strokeStyle = 'red';
                        ctx.stroke();
                        ctx.font = '16px serif';
                        ctx.textBaseline = 'top';
                        ctx.strokeText(box[i].class, x, y);
                    }
                    
                }
                
            }
            
            });

        
    }

    });
</script>
