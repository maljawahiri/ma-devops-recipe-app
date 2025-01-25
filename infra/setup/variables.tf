variable "tf_state_bucket" {
  description = "Name of S3 bucket in AWS for storing TF state"
  default     = "ma-devops-recipe-app-tf-state"
}

variable "tf_state_lock_table" {
  description = "Name of DynamoDB table for TF state locking"
  default     = "ma-devops-recipe-app-tf-lock"
}

variable "project" {
  description = "Project name for tagging resources"
  default     = "ma-recipe-app-api"
}

variable "contact" {
  description = "Contact name for tagging resources"
  default     = "m.aljawahiri@samsung.com"
}