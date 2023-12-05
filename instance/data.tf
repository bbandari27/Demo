data "aws_ami" "latest_ubuntu" {
  most_recent = true

  owners = ["099720109477"]  # Canonical's AWS account ID for Ubuntu

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-*-amd64-server-*"]  # Adjust for the Ubuntu version you want
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}