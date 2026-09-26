resource "aws_s3_bucket" "frontend" {
  bucket = "kaviyan-serverless-app-frontend-${var.environment}"
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  name = "serverless-app-frontend-${var.environment}"

  description                       = "OAC for serverless app frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend" {

  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "frontend-s3"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  default_cache_behavior {
    target_origin_id = "frontend-s3"

    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = [
      "GET",
      "HEAD"
    ]

    cached_methods = [
      "GET",
      "HEAD"
    ]

    compress = true

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

data "aws_iam_policy_document" "frontend_bucket" {

  statement {
    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.frontend.arn}/*"
    ]

    principals {
      type = "Service"

      identifiers = [
        "cloudfront.amazonaws.com"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.frontend.arn
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.frontend_bucket.json
}

resource "aws_s3_object" "index" {
  bucket = aws_s3_bucket.frontend.id

  key    = "index.html"
  source = "${path.module}/../src/frontend/index.html"

  content_type = "text/html"

  etag = filemd5("${path.module}/../src/frontend/index.html")
}


resource "aws_s3_object" "styles" {
  bucket = aws_s3_bucket.frontend.id

  key    = "styles.css"
  source = "${path.module}/../src/frontend/styles.css"

  content_type = "text/css"

  etag = filemd5("${path.module}/../src/frontend/styles.css")
}


resource "aws_s3_object" "app" {
  bucket = aws_s3_bucket.frontend.id

  key    = "app.js"
  source = "${path.module}/../src/frontend/app.js"

  content_type = "application/javascript"

  etag = filemd5("${path.module}/../src/frontend/app.js")
}