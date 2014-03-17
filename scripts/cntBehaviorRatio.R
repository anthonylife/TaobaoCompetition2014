#!/usr/bin/Rscript

#Copyright [2014] [Wei Zhang]

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

###################################################################
# Date: 2014/3/13                                                 #
# This function compute the ratio of different behaviors          #
###################################################################

library("data.table")
library("rjson")
cat("Loading SETTINGS.json file...")

settings <- fromJSON(file="../SETTINGS.json")
data <- read.csv(settings$TAR_DATA_FILE, head=T)

user_id <- unique(data$user_id)
cnt_behavior <- c(0, 0, 0, 0)

for (id in user_id) {
    user_behavior <- data$type[which(data$user_id == id)]
    for (i in 1:4) {
        cnt_behavior[i] <- cnt_behavior[i] + length(which(user_behavior==(i-1)))
    }
}
print(cnt_behavior)
cnt_behavior <- cnt_behavior / sum(cnt_behavior)
print(cnt_behavior)
plot(cnt_behavior)
