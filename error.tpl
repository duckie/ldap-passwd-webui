<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">

    <link rel="stylesheet" href="/static/bootstrap.min.css">
    <script src="/static/jquery-1.10.2.min.js"></script>
    <script src="/static/bootstrap.min.js"></script>
    <title>{{ page_title }}</title>

  </head>

  <body>
    <main>
      <br/>
      <div class="container centering text-center">
        %for type, text in get('alerts', []):
          <div class="alert {{ type }}">{{ text }}</div>
        %end
      </div>
    </main>
  </body>
</html>
