provider "aws" {
  region = "${var.region}"
}

terraform {
  backend "s3" {
    bucket = "bucket-backend-terraform-caioruiz"
    key    = "backend-list-readers/terraform.tfstate"
    region = "sa-east-1"
  }
}