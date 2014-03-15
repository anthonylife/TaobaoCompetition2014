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
# Date: 2014/3/15                                                 #
# This function compute the ratio of different behaviors          #
###################################################################

library("data.table")
library("rjson")
cat("Loading SETTINGS.json file...\n")

settings <- fromJSON(file="SETTINGS.json")
data <- read.csv(settings$TAR_DATA_FILE, head=T)

testdata <- data[which(data$month==as.integer(settings$SPLIT_TIME)), ]
traindata <- data[which(data$month!=as.integer(settings$SPLIT_TIME)), ]

write.csv(traindata, file=settings$TRAIN_DATA_FILE, row.names = FALSE)
write.csv(testdata, file=settings$TEST_DATA_FILE, row.names = FALSE)
