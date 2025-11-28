package com.hostel.dao;

import com.hostel.config.DBUtil;
import com.hostel.model.Allocation;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class AllocationDAO {

    // Allocate room to student
    public boolean allocateRoom(int studentId, int roomId, Date allocationDate) {
        String insertSql = "INSERT INTO allocations (student_id, room_id, allocation_date) " +
                           "VALUES (?, ?, ?)";
        String getRoomSql = "SELECT capacity, occupied FROM rooms WHERE id = ?";
        String updateRoomSql = "UPDATE rooms SET occupied = ? WHERE id = ?";

        Connection conn = null;
        PreparedStatement psInsert = null;
        PreparedStatement psGetRoom = null;
        PreparedStatement psUpdateRoom = null;
        ResultSet rs = null;

        try {
            conn = DBUtil.getConnection();
            conn.setAutoCommit(false);  // start transaction

            // Check room capacity
            psGetRoom = conn.prepareStatement(getRoomSql);
            psGetRoom.setInt(1, roomId);
            rs = psGetRoom.executeQuery();

            if (!rs.next()) {
                conn.rollback();
                return false; // room not found
            }

            int capacity = rs.getInt("capacity");
            int occupied = rs.getInt("occupied");

            if (occupied >= capacity) {
                conn.rollback();
                return false; // room full
            }

            // Insert allocation
            psInsert = conn.prepareStatement(insertSql);
            psInsert.setInt(1, studentId);
            psInsert.setInt(2, roomId);
            psInsert.setDate(3, allocationDate);

            int rows = psInsert.executeUpdate();
            if (rows <= 0) {
                conn.rollback();
                return false;
            }

            // Update room occupied count
            int newOccupied = occupied + 1;
            psUpdateRoom = conn.prepareStatement(updateRoomSql);
            psUpdateRoom.setInt(1, newOccupied);
            psUpdateRoom.setInt(2, roomId);

            int rowsUpdate = psUpdateRoom.executeUpdate();
            if (rowsUpdate <= 0) {
                conn.rollback();
                return false;
            }

            conn.commit();
            return true;

        } catch (SQLException e) {
            e.printStackTrace();
            try {
                if (conn != null) conn.rollback();
            } catch (SQLException ex) {
                ex.printStackTrace();
            }
        } finally {
            try { if (rs != null) rs.close(); } catch (SQLException ignored) {}
            try { if (psInsert != null) psInsert.close(); } catch (SQLException ignored) {}
            try { if (psGetRoom != null) psGetRoom.close(); } catch (SQLException ignored) {}
            try { if (psUpdateRoom != null) psUpdateRoom.close(); } catch (SQLException ignored) {}
            try { if (conn != null) conn.setAutoCommit(true); conn.close(); } catch (SQLException ignored) {}
        }
        return false;
    }

    // Get all allocations (basic list)
    public List<Allocation> getAllAllocations() {
        List<Allocation> list = new ArrayList<>();
        String sql = "SELECT * FROM allocations";

        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {

            while (rs.next()) {
                Allocation a = new Allocation();
                a.setId(rs.getInt("id"));
                a.setStudentId(rs.getInt("student_id"));
                a.setRoomId(rs.getInt("room_id"));
                a.setAllocationDate(rs.getDate("allocation_date"));
                list.add(a);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }
}
