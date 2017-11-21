<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">

    <title>{{ page_title }}</title>

    <link rel="stylesheet" href="/static/bootstrap.min.css">
    <script src="/static/jquery-1.10.2.min.js"></script>
    <script src="/static/bootstrap.min.js"></script>
  </head>

  <body>
    <main>
      <div class="centering text-center">
        <h1>{{ page_title }}</h1>
      </div>
      <br/>
      <div class="row">
        <div class="col-sm-4 col-sm-offset-4">
          <form method="post">
            <input id="username" name="username" class="input-lg form-control" value="{{ get('username', '') }}" type="text" placeholder="User Name" autofocus>

            <input id="old-password" name="old-password" class="input-lg form-control" type="password" placeholder="Old Password" required>
            <input id="new-password" name="new-password" class="input-lg form-control" type="password" placeholder="New Password" required>
            <div class="row">
              <div class="col-sm-6">
                <span id="8char" class="glyphicon glyphicon-remove" style="color:#FF0004;"></span> 8 Characters Long<br>
                <span id="ucase" class="glyphicon glyphicon-remove" style="color:#FF0004;"></span> One Uppercase Letter
              </div>
              <div class="col-sm-6">
                <span id="lcase" class="glyphicon glyphicon-remove" style="color:#FF0004;"></span> One Lowercase Letter<br>
                <span id="num" class="glyphicon glyphicon-remove" style="color:#FF0004;"></span> One Number
              </div>
            </div>

            <input id="confirm-password" name="confirm-password" class="input-lg form-control" type="password" placeholder="Repeat Password" required>
            <div class="row">
              <div class="col-sm-12">
                <span id="pwmatch" class="glyphicon glyphicon-remove" style="color:#FF0004;"></span> Passwords Match
              </div>
            </div>
            <input type="submit" id="submit" class="col-xs-12 btn btn-primary btn-load btn-lg" value="Setup Password" disabled>
          </form>
        </div>
      </div>

      <br/>
      <div class="container centering text-center">
        %for type, text in get('alerts', []):
          <div class="alert {{ type }}">{{ text }}</div>
        %end
      </div>
    </main>
    <script type="text/javascript">
    $("input[type=password]").keyup(function(){
        var ucase = new RegExp("[A-Z]+");
    	var lcase = new RegExp("[a-z]+");
    	var num = new RegExp("[0-9]+");
        var len = new Boolean(false);
        var uc = new Boolean(false);
        var lc = new Boolean(false);
        var digit = new Boolean(false);
        var eq = new Boolean(false);
    
    	
    	if($("#new-password").val().length >= 8){
    		$("#8char").removeClass("glyphicon-remove");
    		$("#8char").addClass("glyphicon-ok");
    		$("#8char").css("color","#00A41E");
                len = true;
    	}else{
    		$("#8char").removeClass("glyphicon-ok");
    		$("#8char").addClass("glyphicon-remove");
    		$("#8char").css("color","#FF0004");
                len = false;
    	}
    	
    	if(ucase.test($("#new-password").val())){
    		$("#ucase").removeClass("glyphicon-remove");
    		$("#ucase").addClass("glyphicon-ok");
    		$("#ucase").css("color","#00A41E");
                uc = true;
    	}else{
    		$("#ucase").removeClass("glyphicon-ok");
    		$("#ucase").addClass("glyphicon-remove");
    		$("#ucase").css("color","#FF0004");
                uc = false;
    	}
    	
    	if(lcase.test($("#new-password").val())){
    		$("#lcase").removeClass("glyphicon-remove");
    		$("#lcase").addClass("glyphicon-ok");
    		$("#lcase").css("color","#00A41E");
                lc = true;
    	}else{
    		$("#lcase").removeClass("glyphicon-ok");
    		$("#lcase").addClass("glyphicon-remove");
    		$("#lcase").css("color","#FF0004");
                lc = false;
    	}
    	
    	if(num.test($("#new-password").val())){
    		$("#num").removeClass("glyphicon-remove");
    		$("#num").addClass("glyphicon-ok");
    		$("#num").css("color","#00A41E");
                digit = true;
    	}else{
    		$("#num").removeClass("glyphicon-ok");
    		$("#num").addClass("glyphicon-remove");
    		$("#num").css("color","#FF0004");
                digit = false;
    	}
    	
    	if($("#new-password").val() == $("#confirm-password").val() && $("#new-password").val() != "" && $("#confirm-password").val() != ""){
    		$("#pwmatch").removeClass("glyphicon-remove");
    		$("#pwmatch").addClass("glyphicon-ok");
    		$("#pwmatch").css("color","#00A41E");
                eq = true;
    	}else{
    		$("#pwmatch").removeClass("glyphicon-ok");
    		$("#pwmatch").addClass("glyphicon-remove");
    		$("#pwmatch").css("color","#FF0004");
                eq = false;
    	}
    	if(len == true && lc == true && uc == true && eq == true && digit == true){
    		$("#submit").prop("disabled", false);
    	}else{
    		$("#submit").prop("disabled", true);
    	}
    });
    </script>
  </body>
</html>
