/* ============================================================
   SECTION SWITCH HANDLING
============================================================ */

function showSection(id) {
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(id).classList.add('active');

    if (id === 'studentsSection') {
        loadStudents();
    }
    else if (id === 'roomsSection') {
        loadRooms();
    }
    else if (id === 'allocationSection') {
        loadStudentsDropdown();
        loadAvailableRoomsDropdown();
        loadAllocations();
    }
}

/* ============================================================
   STUDENT MANAGEMENT
============================================================ */

document.getElementById('studentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append('regNo', document.getElementById('regNo').value);
    formData.append('name', document.getElementById('studentName').value);
    formData.append('department', document.getElementById('department').value);
    formData.append('year', document.getElementById('year').value);
    formData.append('phone', document.getElementById('phone').value);
    formData.append('email', document.getElementById('email').value);

    fetch('api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById('studentMsg');
        if (data.status === 'success') {
            msg.textContent = "Student added successfully!";
            msg.className = "message success";
            document.getElementById('studentForm').reset();
            loadStudents();
            loadStudentsDropdown();
        } else {
            msg.textContent = data.message || "Error adding student.";
            msg.className = "message error";
        }
    })
    .catch(err => console.error(err));
});

function loadStudents() {
    fetch('api/students')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#studentsTable tbody');
            tbody.innerHTML = "";

            data.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${s.id}</td>
                    <td>${s.regNo}</td>
                    <td>${s.name}</td>
                    <td>${s.department || ''}</td>
                    <td>${s.year || ''}</td>
                    <td>${s.phone || ''}</td>
                    <td>${s.email || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

/* ============================================================
   ROOM MANAGEMENT
============================================================ */

document.getElementById('roomForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append('blockName', document.getElementById('blockName').value);
    formData.append('roomNo', document.getElementById('roomNo').value);
    formData.append('capacity', document.getElementById('capacity').value);

    fetch('api/rooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById('roomMsg');
        if (data.status === 'success') {
            msg.textContent = "Room added successfully!";
            msg.className = "message success";
            document.getElementById('roomForm').reset();
            loadRooms();
            loadAvailableRoomsDropdown();
        } else {
            msg.textContent = data.message || "Error adding room.";
            msg.className = "message error";
        }
    })
    .catch(err => console.error(err));
});

function loadRooms() {
    fetch('api/rooms')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#roomsTable tbody');
            tbody.innerHTML = "";

            data.forEach(r => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${r.id}</td>
                    <td>${r.blockName}</td>
                    <td>${r.roomNo}</td>
                    <td>${r.capacity}</td>
                    <td>${r.occupied}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

/* ============================================================
   ALLOCATION MANAGEMENT
============================================================ */

function loadStudentsDropdown() {
    fetch('api/students')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('studentSelect');
            select.innerHTML = "<option value=''>-- Select Student --</option>";

            data.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = `${s.regNo} - ${s.name}`;
                select.appendChild(opt);
            });
        });
}

function loadAvailableRoomsDropdown() {
    fetch('api/rooms?type=available')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('roomSelect');
            select.innerHTML = "<option value=''>-- Select Room --</option>";

            data.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.id;
                opt.textContent = `${r.blockName} - ${r.roomNo} ( ${r.occupied}/${r.capacity} )`;
                select.appendChild(opt);
            });
        });
}

document.getElementById('allocationForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append('studentId', document.getElementById('studentSelect').value);
    formData.append('roomId', document.getElementById('roomSelect').value);

    fetch('api/allocations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
        body: formData.toString()
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById('allocationMsg');
        if (data.status === 'success') {
            msg.textContent = "Room allocated successfully!";
            msg.className = "message success";
            loadAllocations();
            loadAvailableRoomsDropdown();
        } else {
            msg.textContent = data.message || "Room allocation failed.";
            msg.className = "message error";
        }
    })
    .catch(err => console.error(err));
});

function loadAllocations() {
    fetch('api/allocations')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#allocationsTable tbody');
            tbody.innerHTML = "";

            data.forEach(a => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${a.id}</td>
                    <td>${a.studentName || ''}</td>
                    <td>${a.studentRegNo || ''}</td>
                    <td>${a.blockName || ''}</td>
                    <td>${a.roomNo || ''}</td>
                    <td>${a.allocationDate}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

/* ============================================================
   LOAD INITIAL DATA
============================================================ */

window.onload = function () {
    loadStudents();
    loadRooms();
};
