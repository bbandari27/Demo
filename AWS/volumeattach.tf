# Create Temporary Volume
resource "aws_volume" "temp_volume" {
  availability_zone = "your_az"
  size             = 50  # adjust size accordingly
}

# Create Snapshot of Existing Volume
resource "aws_volume_attachment" "existing_volume_attachment" {
  device_name = "/dev/nvme0n1"  # adjust device name accordingly
  volume_id   = "existing_volume_id"
  instance_id = "existing_instance_id"
}

resource "aws_snapshot" "existing_volume_snapshot" {
  volume_id = aws_volume_attachment.existing_volume_attachment.volume_id
}

# Write Snapshot to New Volume
resource "aws_volume" "new_volume" {
  availability_zone = "your_az"
  size             = 100  # adjust size accordingly
  snapshot_id      = aws_snapshot.existing_volume_snapshot.id
}

# Delete Files on New Volume
resource "null_resource" "delete_files" {
  triggers = {
    instance_ids = aws_instance.your_instance_ids[*].id
  }

  provisioner "remote-exec" {
    inline = [
      "rm -rf /data/*",  # assuming data is mounted at /data on the new instance
    ]
  }
}

# Create /data directory on the new instance
resource "aws_instance" "your_instance_ids" {
  # Your existing instance configuration goes here

  user_data = <<-EOF
              #!/bin/bash
              mkdir /data
              EOF
}

# Snapshot the New Volume as Empty
resource "aws_snapshot" "empty_volume_snapshot" {
  volume_id = aws_volume.new_volume.id
}

resource "aws_instance" "aws_syslogfwd03_terraform" {
  ami           = data.aws_ami.ubuntu.id
  associate_public_ip_address          = false
  iam_instance_profile                 = var.iam_instance_profile
  instance_type = var.instance_type
  key_name      = var.key_name
  subnet_id     = var.subnet_id
  // Block Device Mappings
  root_block_device {
    delete_on_termination = true
    encrypted             = true
    iops                  = 3000
    kms_key_id            = var.kms_key_id
    throughput            = 125
    volume_size           = 32
    volume_type           = "gp3"
  }
  // Additional EBS Volumes
  ebs_block_device {
    delete_on_termination = false
    encrypted             = true
    snapshot_id           = "*"
    device_name           = "/dev/sda1"
    iops                  = 3000
    kms_key_id            = var.kms_key_id
    throughput            = 0
    volume_type           = "gp3"
    volume_size           = 100
  }
  metadata_options {
    http_endpoint               = "enabled"
    http_protocol_ipv6          = "disabled"
    http_put_response_hop_limit = 1
    http_tokens                 = "required"
    instance_metadata_tags      = "disabled"
  }
  user_data = <<-EOF
              #!/bin/bash
              # Create /data directory
              mkdir -p /data

              # Add entry to /etc/fstab
              echo '/dev/sda1   /data   xfs   defaults,nofail   0   2' | sudo tee -a /etc/fstab
              echo '/dev/sdf   /data   xfs   defaults,nofail   0   2' | sudo tee -a /etc/fstab

              # Check for the existence of /dev/sda1
              if [ -e "/dev/sda1" ]; then
                  echo "Volume /dev/sda1 exists."
              else
                  echo "Error: Volume /dev/sda1 not found. Please check the instance configuration."
                  exit 1
              fi

              # Mount the volume
              mount -a

              # Check if the volume is mounted
              if mountpoint -q /data; then
                  echo "Volume successfully mounted at /data."
              else
                  echo "Error: Volume mount at /data failed."
              fi
              EOF
  // Security Groups
  vpc_security_group_ids = var.security_group_ids
  // Private IP Addresses
  #  private_ip = "10.110.3.159"
  // Tags
  tags = merge(
    local.ec2_tags,
    {
      Name            = "aws-syslogfwd03-terraform"
    }
  )
}
