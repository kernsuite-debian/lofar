/**
 * Copyright (C) 2018
 * ASTRON (Netherlands Foundation for Research in Astronomy)
 * P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * $Id$
 */


//# Always #include <lofar_config.h> first!
#include <lofar_config.h>

#include <iostream>
#include <unistd.h>
#include <cstring>
#include <boost/date_time.hpp>
#include <Common/StringUtil.h>
#include <OTDB/OTDBconnection.h>
#include <libgen.h>


void help(const std::string& programName)
{
    std::cout << "Usage:  "
        << programName
        << " -dDATABASE -hHOSTNAME -uUSERNAME -pPASSWORD\n\n"
            "Query the OTB DB for the VIC treelist.  This can help to spot "
            "inconsistencies in the DB.  Especially when some entry in the DB "
            "contains an illegal value for a time-stamp.\n\n";
    exit(1);

}

void showTreeList(const std::vector< LOFAR::OTDB::OTDBtree >& trees)
{
    const std::size_t size(trees.size());
    std::cout << size << " records\n";

    std::cout
        << "treeID|Classif|Creator   |Creationdate        |Type|Campaign|Starttime           |ModiDate\n"
        << "------+-------+----------+--------------------+----+--------+--------------------+--------------------\n";
    for(std::size_t i(0); i < size; ++i)
    {
        std::cout << LOFAR::formatString(
            "%6d|%7d|%-10.10s|%-20.20s|%4d|%-8.8s|%-20.20s|%s",
                trees[i].treeID(), trees[i].classification,
                trees[i].creator.c_str(),
                boost::posix_time::to_simple_string(
                    trees[i].creationDate).c_str(),
                trees[i].type,
                trees[i].campaign.c_str(),
                boost::posix_time::to_simple_string(
                    trees[i].starttime).c_str(),
                boost::posix_time::to_simple_string(
                    trees[i].modificationDate).c_str())
            << "\n";
    }
}


int main(int argc, char* argv[])
{
    const std::string programName(basename(argv[0]));
    if(argc != 5)
    {
        help(programName);
    }

    std::string dbName;
    std::string hostName;
    std::string pw;
    std::string user;
    int opt(0);
    while((opt = getopt(argc, argv, "d:h:p:u:")) != -1)
    {
        switch(opt)
        {
            case 'd':
                dbName = optarg;
            break;

            case 'h':
                hostName = optarg;
            break;

            case 'p':
                pw = optarg;
            break;

            case 'u':
                user = optarg;
            break;

            default:
            {
                help(programName);
            }
            break;
        }
    }

    std::cout << "Using database "
        << dbName
        << " on host "
        << hostName
        << "\n";

    // Open the database connection
    LOFAR::OTDB::OTDBconnection conn(user, pw, dbName, hostName);

    try
    {
        std::cout << conn << "\n" << "Trying to connect to the database\n";
        if(!conn.connect())
        {
            std::cout << "Connnection failed!\n";
            return (2);
        }
        else if(!conn.isConnected())
        {
            std::cout << "Connnection flag failed!\n";
            return (3);
        }
        else
        {
            std::cout << "Connection succesful: "
                << conn
                << "\n"
                << "Executing \"getTreeList(30,0)\"...\n";
        }

        std::vector< LOFAR::OTDB::OTDBtree > treeList(conn.getTreeList(30, 0));
        const std::size_t size(treeList.size());
        if(size > 0)
        {
            std::cout << "Received "
                << size
                << " rows from the OTB DB.\n";
            showTreeList(treeList);
        }
        else
        {
            std::cout << "Received no rows from the OTB DB!\n"
                << conn.errorMsg()
                << "\n";
        }
    }
    catch(std::exception& ex)
    {
        std::cout << "Unexpected exception: "
            << ex.what()
            << "\nErrormsg: "
            << conn.errorMsg()
            << "\n";
        return (4);
    }

    return (0);
}
