/*
 * Storage.cpp
 *
 * Author         : Alwin de Jong
 * e-mail         : jong@astron.nl
 * Revision       : $Revision$
 * Last change by : $Author$
 * Change date	  : $Date$
 * First creation : 5-aug-2010
 * URL            : $URL: https://svn.astron.nl/ROD/trunk/LOFAR_Scheduler/Storage.cpp $
 *
 */

#include "lofar_scheduler.h"
#include "Storage.h"
#include <QDateTime>
#include "astrodatetime.h"
#include "Controller.h"
#include <map>
#include <algorithm>
#include <cmath>

using std::map;
using std::min;
using std::max;

Storage::Storage() {
}

Storage::~Storage() {
}

bool storageLocationsContains(const storageLocationOptions &locs, int node_id, int raid_id) {
	for (std::vector<std::pair<int, nodeStorageOptions> >::const_iterator it = locs.begin(); it != locs.end(); ++it) {
		if (it->first == node_id) {
			for (std::vector<storageOption>::const_iterator sit = it->second.begin(); sit != it->second.end(); ++sit) {
				if (sit->raidID == raid_id) return true;
			}
		}
	}
	return false;
}

bool Storage::addStorageNode(const std::string &nodeName, int nodeID) {
	if (itsStorageNodes.find(nodeID) == itsStorageNodes.end()) {
		itsStorageNodes[nodeID] = StorageNode(nodeName, nodeID);
		return true;
	}
	else return false;
}

void Storage::addStoragePartition(int nodeID, unsigned short partitionID, const std::string &path, const double &capacity, const double &free_space) {
	QDateTime cT = QDateTime::currentDateTime().toUTC();
	AstroDateTime now(cT.date().day(), cT.date().month(), cT.date().year(),
			cT.time().hour(), cT.time().minute(), cT.time().second());
	itsStorageNodes[nodeID].addPartition(partitionID, path, now, capacity, free_space);
}

void Storage::clearStorageClaims(void) {
	for (storageNodesMap::iterator it = itsStorageNodes.begin(); it != itsStorageNodes.end(); ++it) {
		it->second.clearClaims();
	}
	itsTaskStorageNodes.clear();
	itsLastStorageCheckResult.clear();
}

void Storage::initStorage(void) {
	itsStorageNodes.clear();
	QDateTime cT = QDateTime::currentDateTime().toUTC();
	const hostPartitionsMap &partitions = Controller::theSchedulerSettings.getStoragePartitions();
	const storageHostsMap &nodes = Controller::theSchedulerSettings.getStorageNodes();
	const double &storageNodeBW = Controller::theSchedulerSettings.getStorageNodeBandWidth();
	StorageNode node;
	AstroDateTime now(cT.date().day(), cT.date().month(), cT.date().year(),
			cT.time().hour(), cT.time().minute(), cT.time().second());
	storageHostsMap::const_iterator nit;
	for (hostPartitionsMap::const_iterator it = partitions.begin(); it != partitions.end(); ++it) {
		nit = nodes.find(it->first);
		if (nit != nodes.end()) {
			node.initNode(nit->second, now, storageNodeBW);
			for (dataPathsMap::const_iterator pit = it->second.begin(); pit != it->second.end(); ++pit) {
				node.addPartition(pit->first, pit->second.first, now, pit->second.second[0], pit->second.second[3]);
			}
			itsStorageNodes[it->first] = node;
			node.clear();
		}
	}
}


// function checkAssignedTaskStorage is used for checking if the given task it's claims are registered at the storage nodes assigned to the task
// assuming it is not possible to assign storage to a task if a conflict arises from it, the function doesn't check if the size and bandwidth requirements are fulfilled.
// it assumes that if the task has been registered at the assigned storage nodes that everything is fine.
std::vector<storageResult> Storage::checkAssignedTaskStorage(Task *pTask, dataProductTypes dataProduct) {
    if (pTask->hasStorage()) {
        const storageMap &storageLocations = pTask->storage()->getStorageLocations();
        storageNodesMap::const_iterator snit;
        storageMap::const_iterator stit = storageLocations.find(dataProduct);
        itsLastStorageCheckResult.clear();
        unsigned int taskID(pTask->getID());
        if (stit != storageLocations.end()) {
            for (storageVector::const_iterator sit = stit->second.begin(); sit != stit->second.end(); ++sit) {
                snit = itsStorageNodes.find(sit->first);
                if (snit != itsStorageNodes.end()) {
                    if (!snit->second.checkClaim(taskID, dataProduct, sit->second)) {
                        itsLastStorageCheckResult.push_back(storageResult(dataProduct, sit->first, sit->second, CONFLICT_NO_STORAGE_ASSIGNED));
                        pTask->setConflict(CONFLICT_NO_STORAGE_ASSIGNED);
                    }
                }
                else {
                    itsLastStorageCheckResult.push_back(storageResult(dataProduct, sit->first, sit->second, CONFLICT_STORAGE_NODE_INEXISTENT));
                    pTask->setConflict(CONFLICT_STORAGE_NODE_INEXISTENT);
                }
            }
        }
        else {
            std::cerr << "Storage::checkAssignedTaskStorage, Warning: data product " << DATA_PRODUCTS[dataProduct] << " not specified for task:" << pTask->getID() << std::endl;
        }
    }
    return itsLastStorageCheckResult;
}


storageLocationOptions Storage::getStorageLocationOptions(dataProductTypes dataProduct, const AstroDateTime &startTime, const AstroDateTime &endTime,
		const double &fileSize, const double &bandWidth, unsigned minNrFiles, sortMode sort_mode, const std::vector<int> &nodes) {
	storageLocationOptions locations;
	itsLastStorageCheckResult.clear();
	nodeStorageOptions node_options;
	std::vector<std::pair<int, task_conflict> > checkResult; // raidID, conflict
	// randomize the storage nodes sequence so that storage nodes with the same number of claims are selected at random
	std::vector<int> randomizedStorageNodes;
	storageNodesMap::const_iterator sit;
	for (std::vector<int>::const_iterator it = nodes.begin(); it != nodes.end(); ++it) {
		sit = itsStorageNodes.find(*it);
		if (sit != itsStorageNodes.end()) {
			if (sit->second.mayBeUsed()) {
				randomizedStorageNodes.push_back(*it);
			}
		}
	}
	std::random_shuffle( randomizedStorageNodes.begin(), randomizedStorageNodes.end() );

	for (std::vector<int>::const_iterator it = randomizedStorageNodes.begin(); it != randomizedStorageNodes.end(); ++it) {
		sit = itsStorageNodes.find(*it);
		checkResult.clear();
		node_options = sit->second.getPossibleRaidArrays(startTime, endTime, fileSize, bandWidth, minNrFiles, checkResult);
		if (!node_options.empty()) {
			locations.push_back(storageLocationOptions::value_type(sit->first, node_options));
		}
		if (!checkResult.empty()) {
			for (std::vector<std::pair<int, task_conflict> >::const_iterator chit = checkResult.begin(); chit != checkResult.end(); ++chit) {
				itsLastStorageCheckResult.push_back(storageResult(dataProduct, sit->first, chit->first, chit->second));
			}
		}
	}
	// sorting requested?
	if (sort_mode == SORT_USAGE) {
		bool inserted;
		storageLocationOptions sortedLocs;
		for (storageLocationOptions::const_iterator slit = locations.begin(); slit != locations.end(); ++slit) {
			inserted = false;
			for (storageLocationOptions::iterator svit = sortedLocs.begin(); svit != sortedLocs.end(); ++svit) {
				if (itsStorageNodes.find(slit->first)->second.nrClaims() < itsStorageNodes.find(svit->first)->second.nrClaims()) {
					sortedLocs.insert(svit, storageLocationOptions::value_type(*slit));
					inserted = true;
					break;
				}
			}
			if (!inserted) {
				sortedLocs.push_back(storageLocationOptions::value_type(*slit));
			}
		}
		return sortedLocs;
	}

	return locations;
}

void Storage::setAllowedStorageHosts(const std::vector<int> &allowedStorageHosts) {
	std::vector<int>::const_iterator it;
	storageNodesMap::iterator sit = itsStorageNodes.begin();
	while (sit != itsStorageNodes.end()) {
		it = find(allowedStorageHosts.begin(),allowedStorageHosts.end(),sit->second.getID());
		if (it != allowedStorageHosts.end()) {
			sit->second.setMayBeUsed(true);
		}
		else {
			sit->second.setMayBeUsed(false);
		}
		++sit;
	}
}
