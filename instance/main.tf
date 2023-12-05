provider "aws" {
  region = var.aws_region
}

data "template_file" "user_data1" {
  template = file(var.user_data_file_path1)
}

data "template_file" "user_data2" {
  template = file(var.user_data_file_path2)
}

resource "aws_instance" "example_instance1" {
  ami           = data.aws_ami.latest_ubuntu.id
  instance_type = var.instance_type1
  key_name      = var.key_name
  subnet_id     = var.subnet_id

  user_data = data.template_file.user_data1.rendered

  security_group_ids = var.security_group_ids

  // Block Device Mappings
  root_block_device {
    volume_type = "gp2"
    volume_size = 8
  }

  // Additional EBS Volumes
  ebs_block_device {
    device_name           = "/dev/sdb"
    volume_type           = "standard"
    volume_size           = 50
    delete_on_termination = false
  }

  // Network Interfaces
  network_interface {
    network_interface_id = "eni-004b898064d066ca"  # Replace with your actual network interface ID
    subnet_id            = var.subnet_id

    // Security Groups
    security_groups = var.security_group_ids

    // Private IP Addresses
    private_ips = ["10.110.3.159"]  # Replace with your actual private IP addresses
  }

  // Tags
  tags = {
    Name            = "aws-syslogfwd01"
    servicegroup    = "syslog"
    costcode        = "905"
    "Patch Group"   = "ubuntu-patch"
    // Add any additional tags here
  }
}

resource "aws_instance" "example_instance2" {
  ami           = data.aws_ami.latest_ubuntu.id
  instance_type = var.instance_type2
  key_name      = var.key_name
  subnet_id     = var.subnet_id

  user_data = data.template_file.user_data2.rendered

  security_group_ids = var.security_group_ids

  // Block Device Mappings
  root_block_device {
    volume_type = "gp2"
    volume_size = 8
  }

  // Additional EBS Volumes
  ebs_block_device {
    device_name           = "/dev/sdb"
    volume_type           = "standard"
    volume_size           = 50
    delete_on_termination = false
  }

  // Network Interfaces
  network_interface {
    network_interface_id = "eni-004b898064d066ca"  # Replace with your actual network interface ID
    subnet_id            = var.subnet_id

    // Security Groups
    security_groups = var.security_group_ids

    // Private IP Addresses
    private_ips = ["10.110.3.159"]  # Replace with your actual private IP addresses
  }

  // Tags
  tags = {
    Name            = "aws-syslogfwd03"
    servicegroup    = "syslog"
    costcode        = "905"
    "Patch Group"   = "ubuntu-patch"
    // Add any additional tags here
  }
}
