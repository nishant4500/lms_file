import { FormEvent, useEffect, useMemo, useState } from "react";
import { HashRouter, Link, Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";

type Role = "student" | "instructor" | "admin";
type Course = { id: number; title: string; description: string; instructor_id: number };
type Module = { id: number; title: string; content: string; course_id: number };
type Resource = { id: number; title: string; url: string; resource_type: "video" | "file" | "link"; module_id: number };

type Option = { id: number; text: string; is_correct?: boolean };
type Question = { id: number; text: string; options: Option[] };
type Quiz = { id: number; title: string; course_id: number; questions: Question[] };
type Certificate = { id: number; student_id: number; course_id: number; issue_date: string };

type UserSession = { token: string; role: Role; userId: number; name: string };

const API_BASE = import.meta.env.DEV ? "http://localhost:8000" : "";

async function api<T>(path: string, init?: RequestInit, token?: string): Promise<T> {
  const headers = new Headers(init?.headers ?? {});
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  
  if (res.status === 401) {
    clearSession();
    window.location.hash = "/login";
    throw new Error("Could not validate credentials. Please login again.");
  }
  
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
    void api<Course[]>("/courses", undefined, session?.token).then(setCourses).catch((e: Error) => setMsg(e.message));
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
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [activeCert, setActiveCert] = useState<Certificate | null>(null);

  if (!session || session.role !== "student") return <Navigate to="/login" replace />;

  useEffect(() => {
    void api<Course[]>("/me/enrollments", undefined, session.token).then(setCourses);
    void api<Certificate[]>("/certificates/me", undefined, session.token).then(setCertificates);
  }, [session.token]);

  return (
    <Shell title="My Learning">
      {activeCert && <CertificateView cert={activeCert} onClose={() => setActiveCert(null)} />}
      
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

      {certificates.length > 0 && (
        <section className="panel premium">
          <div className="heroGlow" style={{ opacity: 0.3 }} />
          <h2>My Certificates</h2>
          <div className="list">
            {certificates.map((cert) => (
              <article className="listItem" key={cert.id}>
                <div>
                  <h3>{cert.course_title || "Course Completion Certificate"}</h3>
                  <p>Issued on: {cert.issue_date}</p>
                </div>
                <button className="secondary" onClick={() => setActiveCert(cert)}>
                  View & Print
                </button>
              </article>
            ))}
          </div>
        </section>
      )}
    </Shell>
  );
}

function QuizTaker({ quiz, onComplete }: { quiz: Quiz; onComplete: (score: number) => void }) {
  const session = getSession();
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [msg, setMsg] = useState("");

  async function onSubmit() {
    if (!session) return;
    const answerIds = Object.values(answers);
    if (answerIds.length < quiz.questions.length) {
      setMsg("Please answer all questions.");
      return;
    }
    try {
      const res = await api<{ score: number }>(`/quizzes/${quiz.id}/attempt`, {
        method: "POST",
        body: JSON.stringify({ quiz_id: quiz.id, answers: answerIds })
      }, session.token);
      onComplete(res.score);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed to submit");
    }
  }

  return (
    <div className="panel premium">
      <h3>Quiz: {quiz.title}</h3>
      <p className="hint">{msg}</p>
      <div className="list">
        {quiz.questions.map((q) => (
          <div key={q.id} style={{ marginBottom: "1rem" }}>
            <p><strong>{q.text}</strong></p>
            {q.options.map((opt) => (
              <label key={opt.id} style={{ display: "block", cursor: "pointer", padding: "5px" }}>
                <input
                  type="radio"
                  name={`q-${q.id}`}
                  onChange={() => setAnswers({ ...answers, [q.id]: opt.id })}
                />
                {" "}{opt.text}
              </label>
            ))}
          </div>
        ))}
      </div>
      <button onClick={onSubmit}>Submit Quiz</button>
    </div>
  );
}

function CertificateView({ cert, onClose }: { cert: any; onClose: () => void }) {
  const session = getSession();
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.85)", zIndex: 9999, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "20px" }}>
       <div className="certificate">
          <h1>Certificate</h1>
          <h2>of Completion</h2>
          <p>This is to certify that</p>
          <div className="name">{session?.userName || "Student"}</div>
          <p>has successfully completed the course</p>
          <div className="course">{cert.course_title || `Course ID: ${cert.course_id}`}</div>
          <p>Issued on {cert.issue_date}</p>
          <div className="seal">OFFICIAL SEAL</div>
       </div>
       <div style={{ marginTop: "20px", display: "flex", gap: "10px" }}>
          <button onClick={() => window.print()}>Print / Save as PDF</button>
          <button className="secondary" onClick={onClose}>Close</button>
       </div>
    </div>
  );
}

function CourseContentPage({ rolePath }: { rolePath: "student" | "instructor" }) {
  const session = getSession();
  const { id } = useParams();
  const [modules, setModules] = useState<Module[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [assignments, setAssignments] = useState<any[]>([]);
  const [progress, setProgress] = useState<any>(null);
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [activeCert, setActiveCert] = useState<any>(null);
  const [submission, setSubmission] = useState("");
  const [msg, setMsg] = useState("");

  if (!session) return <Navigate to="/login" replace />;
  if (rolePath === "student" && session.role !== "student") return <Navigate to="/login" replace />;
  if (rolePath === "instructor" && session.role === "student") return <Navigate to="/login" replace />;

  const reload = () => {
    void api<{ modules: Module[]; resources: Resource[] }>(`/courses/${id}/content`, undefined, session.token)
      .then((d) => {
        setModules(d.modules);
        setResources(d.resources);
      })
      .catch((e: Error) => setMsg(e.message));

    void api<Quiz[]>(`/quizzes/course/${id}`, undefined, session.token)
      .then(setQuizzes)
      .catch(() => {});

    void api<any[]>(`/courses/${id}/assignments`, undefined, session.token)
      .then(setAssignments)
      .catch(() => {});
      
    void api<any[]>(`/progress/me`, undefined, session.token)
      .then(list => setProgress(list.find((p: any) => p.course_id === Number(id))))
      .catch(() => {});

    void api<any[]>("/certificates/me", undefined, session.token)
      .then(list => setActiveCert(list.find((c: any) => c.course_id === Number(id))))
      .catch(() => {});
  };

  useEffect(reload, [id, session.token]);

  return (
    <Shell title="Course Content">
      {activeCert && msg.includes("Certificate Eligible") && (
        <CertificateView cert={activeCert} onClose={() => setMsg("Graduate!")} />
      )}
      
      {activeQuiz ? (
        <QuizTaker
          quiz={activeQuiz}
          onComplete={(score) => {
            setMsg(`Quiz completed! Your score: ${score.toFixed(1)}%`);
            setActiveQuiz(null);
            reload();
          }}
        />
      ) : (
        <>
          {progress && progress.completion_percentage !== undefined && (
            <div className="panel premium" style={{ marginBottom: "1rem", textAlign: "center" }}>
               <h2>Your Progress: {Number(progress.completion_percentage).toFixed(1)}%</h2>
               {progress.completion_percentage >= 70 && (
                 <button onClick={() => setMsg("Certificate Eligible!")} style={{ background: "transparent", color: "var(--primary)", border: "1px solid", padding: "5px 15px", cursor: "pointer" }}>
                   ★ Certificate Eligible! Click to View.
                 </button>
               )}
            </div>
          )}
          
          <section className="split">
            <div className="panel">
              <h2>Modules & Quizzes</h2>
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
              
              {quizzes.length > 0 && (
                <div style={{ marginTop: "2rem" }}>
                  <h3>Available Quizzes</h3>
                  <div className="list">
                    {quizzes.map((q) => (
                      <article className="listItem" key={q.id}>
                        <div>
                          <h4>{q.title}</h4>
                        </div>
                        <button onClick={() => setActiveQuiz(q)}>Take Quiz</button>
                      </article>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="panel">
              <h2>Resources & Assignments</h2>
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

              {assignments.length > 0 && (
                <div style={{ marginTop: "2rem" }}>
                  <h3>Assignments</h3>
                  <div className="list">
                    {assignments.map((a) => (
                      <article className="listItem block" key={a.id}>
                        <div>
                          <h4>{a.title}</h4>
                          <p>{a.description}</p>
                        </div>
                        <div className="grid" style={{ marginTop: "10px" }}>
                          <textarea 
                            placeholder="Type your submission here..." 
                            value={submission}
                            onChange={(e) => setSubmission(e.target.value)}
                          />
                          <button onClick={async () => {
                            try {
                              await api(`/assignments/${a.id}/submit`, {
                                method: "POST",
                                body: JSON.stringify({ content: submission })
                              }, session.token);
                              setSubmission("");
                              setMsg("Assignment submitted!");
                              reload();
                            } catch (e) {
                              setMsg(e instanceof Error ? e.message : "Failed");
                            }
                          }}>Submit</button>
                        </div>
                      </article>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
          
          <div style={{ textAlign: "center", marginTop: "2rem" }}>
             <Link className="secondary" to="/student/my-learning">Return to Dashboard</Link>
          </div>
        </>
      )}
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
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [msg, setMsg] = useState("");

  // Quiz Creator State
  const [quizTitle, setQuizTitle] = useState("");
  const [q1Text, setQ1Text] = useState("");
  const [q1O1, setQ1O1] = useState("");
  const [q1O2, setQ1O2] = useState("");
  const [q1Correct, setQ1Correct] = useState(1);

  if (!session || session.role === "student") return <Navigate to="/login" replace />;

  const reload = () => {
    void api<{ modules: Module[]; resources: Resource[] }>(`/courses/${id}/content`, undefined, session.token)
      .then((d) => {
        setModules(d.modules);
        setResources(d.resources);
        if (d.modules.length > 0 && selectedModuleId === 0) setSelectedModuleId(d.modules[0].id);
      })
      .catch((e: Error) => setMsg(e.message));
    
    void api<Quiz[]>(`/quizzes/course/${id}`, undefined, session.token)
      .then(setQuizzes)
      .catch(() => setQuizzes([]));
  };

  useEffect(reload, [id, session.token]);

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
          </form>

          <div style={{ marginTop: "2rem" }}>
            <h2>Create Quiz</h2>
            <form className="grid" onSubmit={async (e) => {
              e.preventDefault();
              try {
                await api("/quizzes/", {
                  method: "POST",
                  body: JSON.stringify({
                    title: quizTitle,
                    course_id: Number(id),
                    questions: [
                      {
                        text: q1Text,
                        options: [
                          { text: q1O1, is_correct: q1Correct === 1 },
                          { text: q1O2, is_correct: q1Correct === 2 }
                        ]
                      }
                    ]
                  })
                }, session.token);
                setQuizTitle(""); setQ1Text(""); setQ1O1(""); setQ1O2("");
                setMsg("Quiz created successfully.");
                reload();
              } catch (err) {
                setMsg(err instanceof Error ? err.message : "Failed to create quiz");
              }
            }}>
              <input value={quizTitle} onChange={(e) => setQuizTitle(e.target.value)} placeholder="Quiz Title" />
              <input value={q1Text} onChange={(e) => setQ1Text(e.target.value)} placeholder="Question 1 Text" />
              <input value={q1O1} onChange={(e) => setQ1O1(e.target.value)} placeholder="Option 1" />
              <input value={q1O2} onChange={(e) => setQ1O2(e.target.value)} placeholder="Option 2" />
              <select value={q1Correct} onChange={(e) => setQ1Correct(Number(e.target.value))}>
                <option value={1}>Option 1 is correct</option>
                <option value={2}>Option 2 is correct</option>
              </select>
              <button type="submit">Add Quiz</button>
            </form>
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
          
          <p className="hint" style={{ marginTop: "1rem" }}>{msg}</p>
          
          <div className="list">
             <h3>Content List</h3>
            {modules.map((m) => (
              <div key={m.id} style={{ borderBottom: "1px solid #333", padding: "10px 0" }}>
                <p><strong>Module:</strong> {m.title}</p>
                {resources.filter(r => r.module_id === m.id).map(r => (
                  <p key={r.id} style={{ fontSize: "0.8rem", paddingLeft: "10px" }}>📄 {r.title} ({r.resource_type})</p>
                ))}
              </div>
            ))}
            {quizzes.map(q => (
              <div key={q.id} style={{ borderBottom: "1px solid #333", padding: "10px 0", color: "var(--primary)" }}>
                <p><strong>Quiz:</strong> {q.title}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </Shell>
  );
}

export function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
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
