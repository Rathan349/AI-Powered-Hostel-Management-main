package com.hostel.servlet;

import com.hostel.dao.StudentDAO;
import com.hostel.model.Student;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

@WebServlet("/api/students")
public class StudentServlet extends HttpServlet {

    private StudentDAO studentDAO = new StudentDAO();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        Student s = new Student();
        s.setRegNo(request.getParameter("regNo"));
        s.setName(request.getParameter("name"));
        s.setDepartment(request.getParameter("department"));

        String yearStr = request.getParameter("year");
        int year = 0;
        try {
            year = Integer.parseInt(yearStr);
        } catch (NumberFormatException e) {
            year = 0;
        }
        s.setYear(year);

        s.setPhone(request.getParameter("phone"));
        s.setEmail(request.getParameter("email"));

        boolean added = studentDAO.addStudent(s);

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        if (added) {
            out.print("{\"status\":\"success\"}");
        } else {
            out.print("{\"status\":\"error\",\"message\":\"Could not add student\"}");
        }
        out.flush();
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        List<Student> students = studentDAO.getAllStudents();

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        out.print("[");
        for (int i = 0; i < students.size(); i++) {
            Student s = students.get(i);
            out.print("{");
            out.print("\"id\":" + s.getId() + ",");
            out.print("\"regNo\":\"" + s.getRegNo() + "\",");
            out.print("\"name\":\"" + s.getName() + "\",");
            out.print("\"department\":\"" + s.getDepartment() + "\",");
            out.print("\"year\":" + s.getYear() + ",");
            out.print("\"phone\":\"" + s.getPhone() + "\",");
            out.print("\"email\":\"" + s.getEmail() + "\"");
            out.print("}");
            if (i != students.size() - 1) {
                out.print(",");
            }
        }
        out.print("]");
        out.flush();
    }
}
