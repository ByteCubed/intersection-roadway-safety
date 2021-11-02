package org.dotroadsafety.model;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.data.annotation.Id;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Crashes {

    @Id
    @JsonProperty("uid")
    private int uid;
    @JsonProperty("x")
    @JsonAlias("X")
    private double x;
    @JsonProperty("y")
    @JsonAlias("Y")
    private double y;
    @JsonProperty("objectid")
    @JsonAlias("OBJECTID")
    private String objectid;
    @JsonProperty("crimeid")
    @JsonAlias("CRIMEID")
    private String crimeid;
    @JsonProperty("ccn")
    @JsonAlias("CCN")
    private String ccn;
    @JsonProperty("reportdate")
    @JsonAlias("REPORTDATE")
    private String reportdate;
    @JsonProperty("routeid")
    @JsonAlias("ROUTEID")
    private String routeid;
    @JsonProperty("measure")
    @JsonAlias("MEASURE")
    private double measure;
    @JsonProperty("offset")
    @JsonAlias("OFFSET")
    private double offset;
    @JsonProperty("streetsegid")
    @JsonAlias("STREETSEGID")
    private int streetsegid;
    @JsonProperty("roadwaysegid")
    @JsonAlias("ROADWAYSEGID")
    private int roadwaysegid;
    @JsonProperty("fromdate")
    @JsonAlias("FROMDATE")
    private String fromdate;
    @JsonProperty("todate")
    @JsonAlias("TODATE")
    private String todate;
    @JsonProperty("marid")
    @JsonAlias("MARID")
    private String marid;
    @JsonProperty("address")
    @JsonAlias("ADDRESS")
    private String address;
    @JsonProperty("latitude")
    @JsonAlias("LATITUDE")
    private double latitude;
    @JsonProperty("longitude")
    @JsonAlias("LONGITUDE")
    private double longitude;
    @JsonProperty("xcoord")
    @JsonAlias("XCOORD")
    private double xcoord;
    @JsonProperty("ycoord")
    @JsonAlias("YCOORD")
    private double ycoord;
    @JsonProperty("ward")
    @JsonAlias("WARD")
    private String ward;
    @JsonProperty("eventid")
    @JsonAlias("EVENTID")
    private String eventid;
    @JsonProperty("mar_address")
    @JsonAlias("MAR_ADDRESS")
    private String mar_address;
    @JsonProperty("mar_score")
    @JsonAlias("MAR_SCORE")
    private double mar_score;
    @JsonProperty("majorinjuries_bicyclist")
    @JsonAlias("MAJORINJURIES_BICYCLIST")
    private int majorinjuries_bicyclist;
    @JsonProperty("minorinjuries_bicyclist")
    @JsonAlias("MINORINJURIES_BICYCLIST")
    private int minorinjuries_bicyclist;
    @JsonProperty("unknowninjuries_bicyclist")
    @JsonAlias("UNKNOWNINJURIES_BICYCLIST")
    private int unknowninjuries_bicyclist;
    @JsonProperty("fatal_bicyclist")
    @JsonAlias("FATAL_BICYCLIST")
    private int fatal_bicyclist;
    @JsonProperty("majorinjuries_driver")
    @JsonAlias("MAJORINJURIES_DRIVER")
    private int majorinjuries_driver;
    @JsonProperty("minorinjuries_driver")
    @JsonAlias("MINORINJURIES_DRIVER")
    private int minorinjuries_driver;
    @JsonProperty("unknowninjuries_driver")
    @JsonAlias("UNKNOWNINJURIES_DRIVER")
    private int unknowninjuries_driver;
    @JsonProperty("fatal_driver")
    @JsonAlias("FATAL_DRIVER")
    private int fatal_driver;
    @JsonProperty("majorinjuries_pedestrian")
    @JsonAlias("MAJORINJURIES_PEDESTRIAN")
    private int majorinjuries_pedestrian;
    @JsonProperty("minorinjuries_pedestrian")
    @JsonAlias("MINORINJURIES_PEDESTRIAN")
    private int minorinjuries_pedestrian;
    @JsonProperty("unknowninjuries_pedestrian")
    @JsonAlias("UNKNOWNINJURIES_PEDESTRIAN")
    private int unknowninjuries_pedestrian;
    @JsonProperty("fatal_pedestrian")
    @JsonAlias("FATAL_PEDESTRIAN")
    private int fatal_pedestrian;
    @JsonProperty("total_vehicles")
    @JsonAlias("TOTAL_VEHICLES")
    private int total_vehicles;
    @JsonProperty("total_bicycles")
    @JsonAlias("TOTAL_BICYCLES")
    private int total_bicycles;
    @JsonProperty("total_pedestrians")
    @JsonAlias("TOTAL_PEDESTRIANS")
    private int total_pedestrians;
    @JsonProperty("pedestriansimpaired")
    @JsonAlias("PEDESTRIANSIMPAIRED")
    private int pedestriansimpaired;
    @JsonProperty("bicyclistsimpaired")
    @JsonAlias("BICYCLEISTSIMPAIRED")
    private int bicyclistsimpaired;
    @JsonProperty("driversimpaired")
    @JsonAlias("DRIVERSIMPAIRED")
    private int driversimpaired;
    @JsonProperty("total_taxis")
    @JsonAlias("TOTAL_TAXIS")
    private int total_taxis;
    @JsonProperty("total_government")
    @JsonAlias("TOTAL_GOVERMENT")
    private int total_government;
    @JsonProperty("speeding_involved")
    @JsonAlias("SPEEDING_INVOLVED")
    private int speeding_involved;
    @JsonProperty("nearestintrouteid")
    @JsonAlias("NEARESTINTRROUTEID")
    private String nearestintrouteid;
    @JsonProperty("nearestintstreetname")
    @JsonAlias("NEARESTINTSTREETNAME")
    private String nearestintstreetname;
    @JsonProperty("offintersection")
    @JsonAlias("OFFINTERSECTION")
    private double offintersection;
    @JsonProperty("intapproachdirection")
    @JsonAlias("INTAPPROACHDIRECTION")
    private String intapproachdirection;
    @JsonProperty("locationerror")
    @JsonAlias("INTAPPROACHDIRECTION")
    private String locationerror;
    @JsonProperty("lastupdatedate")
    @JsonAlias("LASTUPDATEDATE")
    private String lastupdatedate;
    @JsonProperty("mpdlatitude")
    @JsonAlias("MPDLATITUDE")
    private double mpdlatitude;
    @JsonProperty("mpdlongitude")
    @JsonAlias("PLDLONGITUDE")
    private double mpdlongitude;
    @JsonProperty("mpdgeox")
    @JsonAlias("MPDGEOX")
    private double mpdgeox;
    @JsonProperty("mpdgeoy")
    @JsonAlias("MPDGEOY")
    private double mpdgeoy;
    @JsonProperty("blockkey")
    @JsonAlias("BLOCKKEY")
    private String blockkey;
    @JsonProperty("subblockkey")
    @JsonAlias("SUBBLOCKKEY")
    private String subblockkey;
    @JsonProperty("fatalpassenger")
    @JsonAlias("FATALPASSENGER")
    private int fatalpassenger;
    @JsonProperty("majorinjuriespassenger")
    @JsonAlias("MAJORINJURIESPASSENGER")
    private int majorinjuriespassenger;
    @JsonProperty("minorinjuriespassenger")
    @JsonAlias("MINORINJURIESPASSENGER")
    private int minorinjuriespassenger;
    @JsonProperty("unknowninjuriespassenger")
    @JsonAlias("UNKNOWNINJURIESPASSENGER")
    private int unknowninjuriespassenger;

    public Crashes() {

    }

    public double getX() {
        return x;
    }

    public void setX(double x) {
        this.x = x;
    }

    public double getY() {
        return y;
    }

    public void setY(double y) {
        this.y = y;
    }

    public String getObjectid() {
        return objectid;
    }

    public void setObjectid(String objectid) {
        this.objectid = objectid;
    }

    public String getCrimeid() {
        return crimeid;
    }

    public void setCrimeid(String crimeid) {
        this.crimeid = crimeid;
    }

    public String getCcn() {
        return ccn;
    }

    public void setCcn(String ccn) {
        this.ccn = ccn;
    }

    public String getReportdate() {
        return reportdate;
    }

    public void setReportdate(String reportdate) {
        this.reportdate = reportdate;
    }

    public String getRouteid() {
        return routeid;
    }

    public void setRouteid(String routeid) {
        this.routeid = routeid;
    }

    public double getMeasure() {
        return measure;
    }

    public void setMeasure(double measure) {
        this.measure = measure;
    }

    public double getOffset() {
        return offset;
    }

    public void setOffset(double offset) {
        this.offset = offset;
    }

    public int getStreetsegid() {
        return streetsegid;
    }

    public void setStreetsegid(int streetsegid) {
        this.streetsegid = streetsegid;
    }

    public int getRoadwaysegid() {
        return roadwaysegid;
    }

    public void setRoadwaysegid(int roadwaysegid) {
        this.roadwaysegid = roadwaysegid;
    }

    public String getFromdate() {
        return fromdate;
    }

    public void setFromdate(String fromdate) {
        this.fromdate = fromdate;
    }

    public String getTodate() {
        return todate;
    }

    public void setTodate(String todate) {
        this.todate = todate;
    }

    public String getMarid() {
        return marid;
    }

    public void setMarid(String marid) {
        this.marid = marid;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public double getXcoord() {
        return xcoord;
    }

    public void setCcoord(double xcoord) {
        this.xcoord = xcoord;
    }

    public double getYcoord() {
        return ycoord;
    }

    public void setYcoord(double ycoord) {
        this.ycoord = ycoord;
    }

    public String getWard() {
        return ward;
    }

    public void setWard(String ward) {
        this.ward = ward;
    }

    public String getEventid() {
        return eventid;
    }

    public void setEventid(String eventid) {
        this.eventid = eventid;
    }

    public String getMar_address() {
        return mar_address;
    }

    public void setMar_address(String mar_address) {
        this.mar_address = mar_address;
    }

    public double getMar_score() {
        return mar_score;
    }

    public void setMar_score(double mar_score) {
        this.mar_score = mar_score;
    }

    public int getMajorinjuries_bicyclist() {
        return majorinjuries_bicyclist;
    }

    public void setMajorinjuries_bicyclist(int majorinjuries_bicyclist) {
        this.majorinjuries_bicyclist = majorinjuries_bicyclist;
    }

    public int getMinorinjuries_bicyclist() {
        return minorinjuries_bicyclist;
    }

    public void setMinorinjuries_bicyclist(int minorinjuries_bicyclist) {
        this.minorinjuries_bicyclist = minorinjuries_bicyclist;
    }

    public int getUnknowninjuries_bicyclist() {
        return unknowninjuries_bicyclist;
    }

    public void setUnknowninjuries_bicyclist(int unknowninjuries_bicyclist) {
        this.unknowninjuries_bicyclist = unknowninjuries_bicyclist;
    }

    public int getFatal_bicyclist() {
        return fatal_bicyclist;
    }

    public void setFatal_bicyclist(int fatal_bicyclist) {
        this.fatal_bicyclist = fatal_bicyclist;
    }

    public int getMajorinjuries_driver() {
        return majorinjuries_driver;
    }

    public void setMajorinjuries_driver(int majorinjuries_driver) {
        this.majorinjuries_driver = majorinjuries_driver;
    }

    public int getMinorinjuries_driver() {
        return minorinjuries_driver;
    }

    public void setMinorinjuries_driver(int minorinjuries_driver) {
        this.minorinjuries_driver = minorinjuries_driver;
    }

    public int getUnknowninjuries_driver() {
        return unknowninjuries_driver;
    }

    public void setUnknowninjuries_driver(int unknowninjuries_driver) {
        this.unknowninjuries_driver = unknowninjuries_driver;
    }

    public int getFatal_driver() {
        return fatal_driver;
    }

    public void setFatal_driver(int fatal_driver) {
        this.fatal_driver = fatal_driver;
    }

    public int getMajorinjuries_pedestrian() {
        return majorinjuries_pedestrian;
    }

    public void setMajorinjuries_pedestrian(int majorinjuries_pedestrian) {
        this.majorinjuries_pedestrian = majorinjuries_pedestrian;
    }

    public int getMinorinjuries_pedestrian() {
        return minorinjuries_pedestrian;
    }

    public void setMinorinjuries_pedestrian(int minorinjuries_pedestrian) {
        this.minorinjuries_pedestrian = minorinjuries_pedestrian;
    }

    public int getUnknowninjuries_pedestrian() {
        return unknowninjuries_pedestrian;
    }

    public void setUnknowninjuries_pedestrian(int unknowninjuries_pedestrian) {
        this.unknowninjuries_pedestrian = unknowninjuries_pedestrian;
    }

    public int getFatal_pedestrian() {
        return fatal_pedestrian;
    }

    public void setFatal_pedestrian(int fatal_pedestrian) {
        this.fatal_pedestrian = fatal_pedestrian;
    }

    public int getTotal_vehicles() {
        return total_vehicles;
    }

    public void setTotal_vehicles(int total_vehicles) {
        this.total_vehicles = total_vehicles;
    }

    public int getTotal_bicycles() {
        return total_bicycles;
    }

    public void setTotal_bicycles(int total_bicycles) {
        this.total_bicycles = total_bicycles;
    }

    public int getTotal_pedestrians() {
        return total_pedestrians;
    }

    public void setTotal_pedestrians(int total_pedestrians) {
        this.total_pedestrians = total_pedestrians;
    }

    public int getPedestriansimpaired() {
        return pedestriansimpaired;
    }

    public void setPedestriansimpaired(int pedestriansimpaired) {
        this.pedestriansimpaired = pedestriansimpaired;
    }

    public int getBicyclistsimpaired() {
        return bicyclistsimpaired;
    }

    public void setBicyclistsimpaired(int bicyclistsimpaired) {
        this.bicyclistsimpaired = bicyclistsimpaired;
    }

    public int getDriversimpaired() {
        return driversimpaired;
    }

    public void setDriversimpaired(int driversimpaired) {
        this.driversimpaired = driversimpaired;
    }

    public int getTotal_taxis() {
        return total_taxis;
    }

    public void setTotal_taxis(int total_taxis) {
        this.total_taxis = total_taxis;
    }

    public int getTotal_government() {
        return total_government;
    }

    public void setTotal_government(int total_government) {
        this.total_government = total_government;
    }

    public int getSpeeding_involved() {
        return speeding_involved;
    }

    public void setSpeeding_involved(int speeding_involved) {
        this.speeding_involved = speeding_involved;
    }

    public String getNearestintrouteid() {
        return nearestintrouteid;
    }

    public void setNearestintrouteid(String nearestintrouteid) {
        this.nearestintrouteid = nearestintrouteid;
    }

    public String getNearestintstreetname() {
        return nearestintstreetname;
    }

    public void setNearestintstreetname(String nearestintstreetname) {
        this.nearestintstreetname = nearestintstreetname;
    }

    public double getOffintersection() {
        return offintersection;
    }

    public void setOffintersection(double offintersection) {
        this.offintersection = offintersection;
    }

    public String getIntapproachdirection() {
        return intapproachdirection;
    }

    public void setIntapproachdirection(String intapproachdirection) {
        this.intapproachdirection = intapproachdirection;
    }

    public String getLocationerror() {
        return locationerror;
    }

    public void setLocationerror(String locationerror) {
        this.locationerror = locationerror;
    }

    public String getLastupdatedate() {
        return lastupdatedate;
    }

    public void setLastupdatedate(String lastupdatedate) {
        this.lastupdatedate = lastupdatedate;
    }

    public double getMpdlatitude() {
        return mpdlatitude;
    }

    public void setMpdlatitude(double mpdlatitude) {
        this.mpdlatitude = mpdlatitude;
    }

    public double getMpdlongitude() {
        return mpdlongitude;
    }

    public void setMpdlongitude(double mpdlongitude) {
        this.mpdlongitude = mpdlongitude;
    }

    public double getMpdgeox() {
        return mpdgeox;
    }

    public void setMpdgeox(double mpdgeox) {
        this.mpdgeox = mpdgeox;
    }

    public double getMpdgeoy() {
        return mpdgeoy;
    }

    public void setMpdgeoy(double mpdgeoy) {
        this.mpdgeoy = mpdgeoy;
    }

    public String getBlockkey() {
        return blockkey;
    }

    public void setBlockkey(String blockkey) {
        this.blockkey = blockkey;
    }

    public String getSubblockkey() {
        return subblockkey;
    }

    public void setSubblockkey(String subblockkey) {
        this.subblockkey = subblockkey;
    }

    public int getFatalpassenger() {
        return fatalpassenger;
    }

    public void setFatalpassenger(int fatalpassenger) {
        this.fatalpassenger = fatalpassenger;
    }

    public int getMajorinjuriespassenger() {
        return majorinjuriespassenger;
    }

    public void setMajorinjuriespassenger(int majorinjuriespassenger) {
        this.majorinjuriespassenger = majorinjuriespassenger;
    }

    public int getMinorinjuriespassenger() {
        return minorinjuriespassenger;
    }

    public void setMinorinjuriespassenger(int minorinjuriespassenger) {
        this.minorinjuriespassenger = minorinjuriespassenger;
    }

    public int getUnknowninjuriespassenger() {
        return unknowninjuriespassenger;
    }

    public void setUnknowninjuriespassenger(int unknowninjuriespassenger) {
        this.unknowninjuriespassenger = unknowninjuriespassenger;
    }

    public int getUid() {
        return uid;
    }

    public void setUid(int uid) {
        this.uid = uid;
    }

    public void setXcoord(double xcoord) {
        this.xcoord = xcoord;
    }
}
