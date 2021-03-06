
#!/usr/bin/env python3
# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

#import lofar.messagebus.Message
from lofar.messagebus.message import MessageContent

LOFAR_STATUS_MSG_TEMPLATE = """
<task>
  <type/>
  <state/>
</task>"""

class TaskFeedbackState(MessageContent):
  def __init__(self, from_, forUser, summary, momID, sasID, status):
    super(TaskFeedbackState, self).__init__(
      from_,
      forUser,
      summary,
      "task.feedback.state",
      "1.0.0",
      momID,
      sasID)

    self.document.insertXML("message.payload", LOFAR_STATUS_MSG_TEMPLATE)

    self.type_ = "pipeline"
    if status:
      self.state = "finished"
    else:
      self.state = "aborted"

  def _property_list(self):
     properties = super(TaskFeedbackState, self)._property_list()
     
     properties.update( {
       "type_": "message.payload.task.type",
       "state": "message.payload.task.state",
     } )

     return properties

if __name__ == "__main__":
    msg = TaskFeedbackState("FROM", "FORUSER", "SUMMARY", "11111", "22222", True)
    print(msg.content())

