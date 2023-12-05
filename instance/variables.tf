variable "aws_region" {
  description = "The AWS region where the EC2 instances will be created."
  type        = string
  default     = "us-east-1"  # Replace with your actual AWS region
}

variable "key_name" {
  description = "The name of the key pair used for the EC2 instances."
  type        = string
  default     = "awselk"  # Replace with your actual key pair name
}

variable "subnet_id" {
  description = "The ID of the subnet where the EC2 instances will be launched."
  type        = string
  default     = "subnet-f79bdfbf"  # Replace with your actual subnet ID
}

variable "security_group_ids" {
  description = "A list of security group IDs for the EC2 instances."
  type        = list(string)
  default     = ["sg-008ecdedc4d427e2e", "sg-00b075f3ecc35fe09"]  # Replace with your actual security group IDs
}

variable "instance_type1" {
  description = "The type of the first EC2 instance to launch."
  type        = string
  default     = "t3.small"  # Replace with your actual instance type
}

variable "instance_type2" {
  description = "The type of the second EC2 instance to launch."
  type        = string
  default     = "t3.small"  # Replace with your actual instance type
}

variable "user_data_file_path1" {
  description = "Path to the user data script file for the first instance."
  type        = string
  default     = "./userdata1.sh"  # Update if your file is in a different location
}

variable "user_data_file_path2" {
  description = "Path to the user data script file for the second instance."
  type        = string
  default     = "./userdata2.sh"  # Update if your file is in a different location
}
