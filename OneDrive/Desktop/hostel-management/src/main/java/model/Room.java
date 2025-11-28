package com.hostel.model;

public class Room {
    private int id;
    private String blockName;
    private String roomNo;
    private int capacity;
    private int occupied;

    public Room() {
    }

    public Room(int id, String blockName, String roomNo, int capacity, int occupied) {
        this.id = id;
        this.blockName = blockName;
        this.roomNo = roomNo;
        this.capacity = capacity;
        this.occupied = occupied;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getBlockName() {
        return blockName;
    }

    public void setBlockName(String blockName) {
        this.blockName = blockName;
    }

    public String getRoomNo() {
        return roomNo;
    }

    public void setRoomNo(String roomNo) {
        this.roomNo = roomNo;
    }

    public int getCapacity() {
        return capacity;
    }

    public void setCapacity(int capacity) {
        this.capacity = capacity;
    }

    public int getOccupied() {
        return occupied;
    }

    public void setOccupied(int occupied) {
        this.occupied = occupied;
    }
}
