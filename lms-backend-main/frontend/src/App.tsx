import { FormEvent, useEffect, useMemo, useState } from "react";
import { HashRouter, Link, Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";

type Role = "student" | "instructor" | "admin";
type Course = { id: number; title: string; description: string; instructor_id: number };
type Module = { id: number; title: string; content: string; course_id: number };
type Resource = { id: number; title: string; url: string; resource_type: "video" | "file" | "link"; module_id: number };
type UserSession = { token: string; role: Role; userId: number; name: string };

const API_BASE = import.meta.env.DEV ? "http://127.0.0.1:8000" : "";

async function api<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const headers = new Headers(init?.headers ?? {});
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ?? "Request failed");
  return data as T;
}

function getSession(): UserSession | null {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role") as Role | null;
  const userId = Number(localStorage.getItem("user_id") ?? 0);
  const name = localStorage.getItem("name") ?? "";
  if (!token || !role || !userId) return null;
  return { token, role, userId, name };
}

function setSession(s: UserSession) {
  localStorage.setItem("token", s.token);
  localStorage.setItem("role", s.role);
  localStorage.setItem("user_id", String(s.userId));
  localStorage.setItem("name", s.name);
}

function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("user_id");
  localStorage.removeItem("name");
}

function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  const navigate = useNavigate();
  const session = getSession();
  return (
    <div className="page">
      <header className="hero">
        <div className="heroGlow" />
        <div className="heroContent">
          <p className="kicker">LMS PORTAL</p>
          <h1>{title}</h1>
          <p>Separate pages for clean, role-based workflow.</p>
        </div>
        <div className="session premium">
          <span className="userName">{session?.name ?? "Guest"}</span>
          <span className="badge">{session ? session.role : "Not logged in"}</span>
          {session ? (
            <button
              className="secondary"
              onClick={() => {
                clearSession();
                navigate("/login");
              }}
            >
              Logout
            </button>
          ) : null}
        </div>
      </header>
      {children}
    </div>
  );
}

function RegisterPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("student");
  const [msg, setMsg] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await api("/register", { method: "POST", body: JSON.stringify({ name, email, password, role }) });
      setMsg("Registered successfully. Please login.");
      setTimeout(() => navigate("/login"), 800);
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <Shell title="Create Account">
      <section className="panel authPanel">
        <form className="grid" onSubmit={onSubmit}>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" />
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
          <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
            <option value="student">Student</option>
            <option value="instructor">Instructor</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit">Register</button>
          <p className="hint">{msg}</p>
          <Link to="/login" className="linkBtn">
            Go to Login
          </Link>
        </form>
      </section>
    </Shell>
  );
}

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const data = await api<{ access_token: string; role: Role; user_id: number; name: string }>("/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setSession({ token: data.access_token, role: data.role, userId: data.user_id, name: data.name });
      if (data.role === "student") navigate("/student/courses");
      else navigate("/instructor/courses");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Failed");
    }
  }

  return (
    <Shell title="Welcome Back">
      <section className="panel authPanel">
        <form className="grid" onSubmit={onSubmit}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
          <button type="submit">Login</button>
          <p className="hint">{msg}</p>
          <Link to="/register" className="linkBtn">
            Create Account
          </Link>
        </form>
      </section>
    </Shell>
  );
}

function StudentCoursesPage() {
  const session = getSession();
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [msg, setMsg] = useState("");
  useEffect(() => {
    if (!session) return;
    void api<Course[]>("/courses").then(setCourses).catch((e: Error) => setMsg(e.message));
  }, [session]);
  if (!session || session.role !== "student") return <Navigate to="/login" replace />;
  return (
    <Shell title="Student Courses">
      <section className="panel">
        <div className="panelHead">
          <h2>All Available Courses</h2>
          <button className="secondary" onClick={() => navigate("/student/my-learning")}>
            My Learning
          </button>
        </div>
        <p className="hint">{msg}</p>
        <div className="list">
          {courses.map((c) => (
            <article className="listItem" key={c.id}>
              <div>
                <h3>{c.title}</h3>
                <p>{c.description}</p>
              </div>
              <button
                onClick={async () => {
                  try {
                    await api(`/courses/${c.id}/enroll`, { method: "POST" }, session.token);
                    setMsg("Enrolled successfully.");
                  } catch (e) {
                    setMsg(e instanceof Error ? e.message : "Failed");
                  }
                }}
              >
                Enroll
              </button>
            </article>
          ))}
        </div>
      </section>
    </Shell>
  );
}

function StudentLearningPage() {
  const session = getSession();
  const [courses, setCourses] = useState<Course[]>([]);
  if (!session || session.role !== "student") return <Navigate to="/login" replace />;
  useEffect(() => {
    void api<Course[]>("/me/enrollments", undefined, session.token).then(setCourses);
  }, [session.token]);
  return (
    <Shell title="My Learning">
      <section className="panel">
        <h2>Enrolled Courses</h2>
        <div className="list">
          {courses.map((c) => (
            <article className="listItem" key={c.id}>
              <div>
                <h3>{c.title}</h3>
                <p>{c.description}</p>
              </div>
              <Link className="linkBtn" to={`/student/course/${c.id}`}>
                Open
              </Link>
            </article>
          ))}
        </div>
      </section>
    </Shell>
  );
}

function CourseContentPage({ rolePath }: { rolePath: "student" | "instructor" }) {
  const session = getSession();
  const { id } = useParams();
  const [modules, setModules] = useState<Module[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [msg, setMsg] = useState("");
  if (!session) return <Navigate to="/login" replace />;
  if (rolePath === "student" && session.role !== "student") return <Navigate to="/login" replace />;
  if (rolePath === "instructor" && session.role === "student") return <Navigate to="/login" replace />;
  useEffect(() => {
    void api<{ modules: Module[]; resources: Resource[] }>(`/courses/${id}/content`, undefined, session.token)
      .then((d) => {
        setModules(d.modules);
        setResources(d.resources);
      })
      .catch((e: Error) => setMsg(e.message));
  }, [id, session.token]);
  return (
    <Shell title="Course Content">
      <section className="split">
        <div className="panel">
          <h2>Modules</h2>
          <p className="hint">{msg}</p>
          <div className="list">
            {modules.map((m) => (
              <article className="listItem" key={m.id}>
                <div>
                  <h3>{m.title}</h3>
                  <p>{m.content}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
        <div className="panel">
          <h2>Resources</h2>
          <div className="list">
            {resources.map((r) => (
              <article className="listItem" key={r.id}>
                <div>
                  <h3>{r.title}</h3>
                  <p>{r.resource_type}</p>
                </div>
                <a className="linkBtn" href={r.url} target="_blank" rel="noreferrer">
                  Open
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>
    </Shell>
  );
}

function InstructorCoursesPage() {
  const session = getSession();
  const [courses, setCourses] = useState<Course[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [msg, setMsg] = useState("");
  const myCourses = useMemo(
    () => (session?.role === "admin" ? courses : courses.filter((c) => c.instructor_id === session?.userId)),
    [courses, session]
  );
  if (!session || session.role === "student") return <Navigate to="/login" replace />;
  const reload = () => void api<Course[]>("/courses").then(setCourses);
  useEffect(reload, []);
  return (
    <Shell title="Instructor Dashboard">
      <section className="panel">
        <h2>Create Course</h2>
        <form
          className="grid"
          onSubmit={async (e) => {
            e.preventDefault();
            try {
              await api("/courses", { method: "POST", body: JSON.stringify({ title, description }) }, session.token);
              setTitle("");
              setDescription("");
              reload();
              setMsg("Course created.");
            } catch (err) {
              setMsg(err instanceof Error ? err.message : "Failed");
            }
          }}
        >
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Course title" />
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Course description" />
          <button type="submit">Create</button>
          <p className="hint">{msg}</p>
        </form>
      </section>

      <section className="panel">
        <h2>My Courses</h2>
        <div className="list">
          {myCourses.map((c) => (
            <article className="listItem" key={c.id}>
              <div>
                <h3>{c.title}</h3>
                <p>{c.description}</p>
              </div>
              <Link className="linkBtn" to={`/instructor/course/${c.id}`}>
                Manage
              </Link>
            </article>
          ))}
        </div>
      </section>
    </Shell>
  );
}

function InstructorCourseManagePage() {
  const session = getSession();
  const { id } = useParams();
  const [moduleTitle, setModuleTitle] = useState("");
  const [moduleContent, setModuleContent] = useState("");
  const [resourceTitle, setResourceTitle] = useState("");
  const [resourceUrl, setResourceUrl] = useState("");
  const [resourceType, setResourceType] = useState<"video" | "file" | "link">("video");
  const [selectedModuleId, setSelectedModuleId] = useState<number>(0);
  const [modules, setModules] = useState<Module[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [msg, setMsg] = useState("");
  if (!session || session.role === "student") return <Navigate to="/login" replace />;

  const reload = () =>
    void api<{ modules: Module[]; resources: Resource[] }>(`/courses/${id}/content`, undefined, session.token)
      .then((d) => {
        setModules(d.modules);
        setResources(d.resources);
        if (d.modules.length > 0 && selectedModuleId === 0) setSelectedModuleId(d.modules[0].id);
      })
      .catch((e: Error) => setMsg(e.message));
  useEffect(reload, []);

  return (
    <Shell title="Manage Course">
      <section className="split">
        <div className="panel">
          <h2>Create Module</h2>
          <form
            className="grid"
            onSubmit={async (e) => {
              e.preventDefault();
              try {
                await api(
                  "/modules",
                  { method: "POST", body: JSON.stringify({ title: moduleTitle, content: moduleContent, course_id: Number(id) }) },
                  session.token
                );
                setModuleTitle("");
                setModuleContent("");
                reload();
                setMsg("Module created.");
              } catch (err) {
                setMsg(err instanceof Error ? err.message : "Failed");
              }
            }}
          >
            <input value={moduleTitle} onChange={(e) => setModuleTitle(e.target.value)} placeholder="Module title" />
            <input value={moduleContent} onChange={(e) => setModuleContent(e.target.value)} placeholder="Module content" />
            <button type="submit">Add Module</button>
            <p className="hint">{msg}</p>
          </form>
          <div className="list">
            {modules.map((m) => (
              <article className="listItem" key={m.id}>
                <div>
                  <h3>{m.title}</h3>
                  <p>{m.content}</p>
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Add Resource</h2>
          <form
            className="grid"
            onSubmit={async (e) => {
              e.preventDefault();
              try {
                await api(
                  "/resources",
                  {
                    method: "POST",
                    body: JSON.stringify({
                      title: resourceTitle,
                      url: resourceUrl,
                      resource_type: resourceType,
                      module_id: selectedModuleId
                    })
                  },
                  session.token
                );
                setResourceTitle("");
                setResourceUrl("");
                reload();
                setMsg("Resource added.");
              } catch (err) {
                setMsg(err instanceof Error ? err.message : "Failed");
              }
            }}
          >
            <select value={selectedModuleId} onChange={(e) => setSelectedModuleId(Number(e.target.value))}>
              {modules.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.title}
                </option>
              ))}
            </select>
            <input value={resourceTitle} onChange={(e) => setResourceTitle(e.target.value)} placeholder="Resource title" />
            <input value={resourceUrl} onChange={(e) => setResourceUrl(e.target.value)} placeholder="Resource URL" />
            <select value={resourceType} onChange={(e) => setResourceType(e.target.value as "video" | "file" | "link")}>
              <option value="video">Video</option>
              <option value="file">File</option>
              <option value="link">Link</option>
            </select>
            <button type="submit">Add Resource</button>
          </form>
          <div className="list">
            {resources.map((r) => (
              <article className="listItem" key={r.id}>
                <div>
                  <h3>{r.title}</h3>
                  <p>{r.resource_type}</p>
                </div>
                <a className="linkBtn" href={r.url} target="_blank" rel="noreferrer">
                  Open
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>
    </Shell>
  );
}

export function App() {
  const session = getSession();
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Navigate to={session ? (session.role === "student" ? "/student/courses" : "/instructor/courses") : "/login"} replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/student/courses" element={<StudentCoursesPage />} />
        <Route path="/student/my-learning" element={<StudentLearningPage />} />
        <Route path="/student/course/:id" element={<CourseContentPage rolePath="student" />} />
        <Route path="/instructor/courses" element={<InstructorCoursesPage />} />
        <Route path="/instructor/course/:id" element={<InstructorCourseManagePage />} />
        <Route path="/instructor/content/:id" element={<CourseContentPage rolePath="instructor" />} />
      </Routes>
    </HashRouter>
  );
}
