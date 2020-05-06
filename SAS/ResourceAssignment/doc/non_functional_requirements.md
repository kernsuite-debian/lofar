# Resource Assignment Non Functional Requirements {#resource_assignment_non_functional_requirements}

# Non Functional Requirements 

This is a list of Non Functional Requirements that have been identified in discussion with Software Support.
These will be input for the redesign that we'll need to do of specification and scheduling tools for responsive telescope.

Non Functional Requirements are those points deemed important that do not directly describe functionality.
The goal is not to argue the points, but to get a list of what the users deem important.

The initial questioned focus on what the good points and possible improvements of the current Scheduler are:

##Good points
  * The current Scheduler is very Robust.
    * It has no bugs. At least none that interfere with day-to-day operations.
    * It's reliable.
    * It's predictable.
    * Unlike some other tools like MoM, it never has unexpected behaviour.
    * It doesn't lie. It represents the true state of the system.
  * It's user friendly.
    * Response is immediate, there are no delays.
    * It's easy to have overviews of everything, but also make detailed sub selections quickly.
    * It quickly responds to queries and selections.
    * Good overviews of all important information.
      * All information in one go.
    * It's fast.
    * You can drill deep into the system with things like the SAS tree view.
      * If needed all information is visible.
      * Nothing is hidden and requires you to go to another tool.
  * The copy option is essential.
    * It's a good tool for quick tests, validation runs.
    * Very quick. You have it directly/immediately.
    * Only 2 clicks.
  * The multi edit is very good.
    * It's essential to do batches of observations or pipelines.
  * It's much easier to get things implemented in the Scheduler than in MoM, at least while Alwin was still here.
    * Alwin listened to Science Operations and Support.
    * Alwin was in the Control Room and knew what the problems were.
    * Alwin's first priority was Science Operations and Support not other development tasks.

##Improvements
  * There are no templates in the Scheduler.
    * You should for example be able to just chose a set of validation runs.
    * Now you have to go through the XML Generator or copy them separately.
    * The same for Station Calibration and other repeating observations like EoR, etc.
  * There is no Batch Scheduling.
    * For pipelines.
    * Time and resources.
  * There is no multi edit for every parameter in OTDB/parset.
  * There is no immediate interation between Northstar, XML Generator, GenvalObs, and other specification tools and the Scheduler/OTDB.
    * Now things get lost between tools.
    * Things need to be copied manually.
    * It's hard to have consistency.
    * We have loops in the system where a change in **A** creates a change in **B** which creates a change in **A**.
    * We have to much interdependence where tools depend on each other.
  * Scheduler should include ingest and cleanup/delete tasks.
  * The system as a whole should be more reliable.
    * There is often no consistency between MoM/OTDB/LTA and other tools.
    * We need more and better feedback on what goes wrong. Clear error messages.
  * It should be nice if you could save a draft of something you're preparing in the Scheduler.
  * You can currently not make changes in OTDB directly for a lot of parameters, but have to go to OTB.
  
### Note

The initial version of this was copied from [RRR Resource Assigner Non functional Requirements](https://www.astron.nl/lofarwiki/doku.php?id=rrr:non_functional_requirements_software_support)
