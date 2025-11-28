package com.hostel.model;

import java.sql.Date;  // from java.sql for JDBC

public class Allocation {
    private int id;
    private int studentId;
    private int roomId;
    private Date allocationDate;

    public Allocation() {
    }

    public Allocation(int id, int studentId, int roomId, Date allocationDate) {
        this.id = id;
        this.studentId = studentId;
        this.roomId = roomId;
        this.allocationDate = allocationDate;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getStudentId() {
        return studentId;
    }

    public void setStudentId(int studentId) {
        this.studentId = studentId;
    }

    public int getRoomId() {
        return roomId;
    }

    public void setRoomId(int roomId) {
        this.roomId = roomId;
    }

    public Date getAllocationDate() {
        return allocationDate;
    }

    public void setAllocationDate(Date allocationDate) {
        this.allocationDate = allocationDate;
    }
}
