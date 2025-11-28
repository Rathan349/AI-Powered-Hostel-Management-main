package com.hostel.servlet;

import com.hostel.dao.AllocationDAO;
import com.hostel.dao.StudentDAO;
import com.hostel.dao.RoomDAO;
import com.hostel.model.Allocation;
import com.hostel.model.Student;
import com.hostel.model.Room;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Date;
import java.util.List;

@WebServlet("/api/allocations")
public class AllocationServlet extends HttpServlet {

    private AllocationDAO allocationDAO = new AllocationDAO();
    private StudentDAO studentDAO = new StudentDAO();
    private RoomDAO roomDAO = new RoomDAO();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String studentIdStr = request.getParameter("studentId");
        String roomIdStr = request.getParameter("roomId");

        int studentId = 0;
        int roomId = 0;

        try {
            studentId = Integer.parseInt(studentIdStr);
            roomId = Integer.parseInt(roomIdStr);
        } catch (NumberFormatException e) {
            // invalid input
        }

        Date today = new Date(System.currentTimeMillis());

        boolean ok = allocationDAO.allocateRoom(studentId, roomId, today);

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        if (ok) {
            out.print("{\"status\":\"success\"}");
        } else {
            out.print("{\"status\":\"error\",\"message\":\"Room full or allocation failed\"}");
        }
        out.flush();
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        List<Allocation> allocations = allocationDAO.getAllAllocations();

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        out.print("[");
        for (int i = 0; i < allocations.size(); i++) {
            Allocation a = allocations.get(i);
            Student s = studentDAO.getStudentById(a.getStudentId());
            Room r = roomDAO.getRoomById(a.getRoomId());

            out.print("{");
            out.print("\"id\":" + a.getId() + ",");
            out.print("\"studentId\":" + a.getStudentId() + ",");
            out.print("\"roomId\":" + a.getRoomId() + ",");
            out.print("\"allocationDate\":\"" + a.getAllocationDate() + "\"");

            // extra info for UI convenience
            if (s != null) {
                out.print(",\"studentName\":\"" + s.getName() + "\"");
                out.print(",\"studentRegNo\":\"" + s.getRegNo() + "\"");
            }
            if (r != null) {
                out.print(",\"blockName\":\"" + r.getBlockName() + "\"");
                out.print(",\"roomNo\":\"" + r.getRoomNo() + "\"");
            }

            out.print("}");
            if (i != allocations.size() - 1) {
                out.print(",");
            }
        }
        out.print("]");
        out.flush();
    }
}
