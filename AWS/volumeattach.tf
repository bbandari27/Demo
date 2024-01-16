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

