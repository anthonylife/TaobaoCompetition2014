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

settings <- fromJSON(file="../SETTINGS.json")
Args <-  commandArgs()

if (is.na(Args[6])) {
    print("Need to specify which method to choose.")
    q()
} 

if (Args[6] == "libmf") {
    traindata <- read.csv(settings$TRAIN_DATA_FILE, head=T)
    trainpair <- traindata[which(traindata$type == 1), c(1, 2)]
    tag <- rep(1, length(trainpair[, 1]))
    formatted_train_data <- cbind(trainpair, tag)
    write.table(formatted_train_data, file=settings$LIBMF_TRAIN_FILE,
                row.names = FALSE,col.names = FALSE, sep = " ")
}
