package com.hostel.dao;

import com.hostel.config.DBUtil;
import com.hostel.model.Student;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class StudentDAO {

    // Insert new student
    public boolean addStudent(Student s) {
        String sql = "INSERT INTO students (reg_no, name, department, year, phone, email) " +
                     "VALUES (?, ?, ?, ?, ?, ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, s.getRegNo());
            ps.setString(2, s.getName());
            ps.setString(3, s.getDepartment());
            ps.setInt(4, s.getYear());
            ps.setString(5, s.getPhone());
            ps.setString(6, s.getEmail());

            return ps.executeUpdate() > 0;   // true if inserted

        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    // Get all students
    public List<Student> getAllStudents() {
        List<Student> list = new ArrayList<>();
        String sql = "SELECT * FROM students";

        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {

            while (rs.next()) {
                Student s = new Student();
                s.setId(rs.getInt("id"));
                s.setRegNo(rs.getString("reg_no"));
                s.setName(rs.getString("name"));
                s.setDepartment(rs.getString("department"));
                s.setYear(rs.getInt("year"));
                s.setPhone(rs.getString("phone"));
                s.setEmail(rs.getString("email"));
                list.add(s);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    // Get one student by ID (useful for allocation)
    public Student getStudentById(int id) {
        String sql = "SELECT * FROM students WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setInt(1, id);
            ResultSet rs = ps.executeQuery();

            if (rs.next()) {
                Student s = new Student();
                s.setId(rs.getInt("id"));
                s.setRegNo(rs.getString("reg_no"));
                s.setName(rs.getString("name"));
                s.setDepartment(rs.getString("department"));
                s.setYear(rs.getInt("year"));
                s.setPhone(rs.getString("phone"));
                s.setEmail(rs.getString("email"));
                return s;
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }
}
