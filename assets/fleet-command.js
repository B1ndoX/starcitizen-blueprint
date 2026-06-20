const root = document.documentElement;
const intro = document.querySelector("[data-intro-sequence]");
const introSticky = document.querySelector("[data-intro-sticky]");
const navLinks = [...document.querySelectorAll("[data-scroll-link]")];
const sections = [...document.querySelectorAll("main section[id]")];
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function smoothRange(progress, start, end) {
  const value = clamp((progress - start) / Math.max(0.001, end - start), 0, 1);
  return value * value * (3 - 2 * value);
}

function initStarfield() {
  const canvas = document.querySelector("#starfieldCanvas");
  if (!canvas || !introSticky) return;

  const context = canvas.getContext("2d", { alpha: true });
  let width = 0;
  let height = 0;
  let stars = [];
  let animationFrame = 0;
  let lastRender = 0;

  function createStars() {
    const compact = window.innerWidth < 720;
    const count = compact ? 145 : 310;
    stars = Array.from({ length: count }, () => ({
      x: Math.random(),
      y: Math.random(),
      z: Math.random() * 0.9 + 0.1,
      size: Math.random() * 1.7 + 0.35,
      drift: Math.random() * 0.28 + 0.06,
      warm: Math.random() > 0.82,
    }));
  }

  function resize() {
    const scale = Math.min(window.devicePixelRatio || 1, 2);
    const box = introSticky.getBoundingClientRect();
    width = Math.max(1, Math.round(box.width));
    height = Math.max(1, Math.round(box.height));
    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    context.setTransform(scale, 0, 0, scale, 0, 0);
    createStars();
  }

  function drawNebula(progress) {
    const blueGlow = context.createRadialGradient(width * 0.72, height * 0.28, 0, width * 0.72, height * 0.28, width * 0.52);
    blueGlow.addColorStop(0, `rgba(95, 168, 211, ${0.13 + progress * 0.04})`);
    blueGlow.addColorStop(0.42, "rgba(95, 168, 211, 0.04)");
    blueGlow.addColorStop(1, "rgba(95, 168, 211, 0)");
    context.fillStyle = blueGlow;
    context.fillRect(0, 0, width, height);

    const goldGlow = context.createRadialGradient(width * 0.23, height * 0.62, 0, width * 0.23, height * 0.62, width * 0.38);
    goldGlow.addColorStop(0, "rgba(200, 164, 93, 0.08)");
    goldGlow.addColorStop(0.5, "rgba(200, 164, 93, 0.025)");
    goldGlow.addColorStop(1, "rgba(200, 164, 93, 0)");
    context.fillStyle = goldGlow;
    context.fillRect(0, 0, width, height);
  }

  function render(time = 0) {
    if (prefersReducedMotion && lastRender) return;
    lastRender = time;
    const progress = Number.parseFloat(intro?.style.getPropertyValue("--intro-progress")) || 0;

    context.clearRect(0, 0, width, height);
    context.fillStyle = "#030508";
    context.fillRect(0, 0, width, height);
    drawNebula(progress);

    context.save();
    context.translate(width / 2, height / 2);

    stars.forEach((star) => {
      const warp = progress * progress * 70 * star.z;
      const drift = prefersReducedMotion ? 0 : (time * 0.000015 * star.drift) % 1;
      const x = (star.x - 0.5) * width * (1 + progress * 0.24) + (star.x - 0.5) * warp;
      const y = (((star.y + drift) % 1) - 0.5) * height * (1 + progress * 0.18) + (star.y - 0.5) * warp * 0.72;
      const alpha = clamp(0.28 + star.z * 0.75 + progress * 0.18, 0.18, 1);
      const length = 1 + progress * 18 * star.z;

      context.beginPath();
      context.strokeStyle = star.warm ? `rgba(200, 164, 93, ${alpha})` : `rgba(242, 245, 247, ${alpha})`;
      context.lineWidth = Math.max(0.45, star.size * star.z);
      context.moveTo(x, y);
      context.lineTo(x + (x > 0 ? length : -length) * 0.36, y + (y > 0 ? length : -length) * 0.16);
      context.stroke();
    });

    context.restore();

    if (!prefersReducedMotion) {
      animationFrame = requestAnimationFrame(render);
    }
  }

  resize();
  render();
  window.addEventListener("resize", resize, { passive: true });
  if (!prefersReducedMotion) animationFrame = requestAnimationFrame(render);

  return () => cancelAnimationFrame(animationFrame);
}

function updateIntroProgress() {
  if (!intro) return;

  if (prefersReducedMotion) {
    intro.style.setProperty("--intro-progress", "1");
    intro.style.setProperty("--intro-title", "1");
    intro.style.setProperty("--intro-motto", "1");
    intro.style.setProperty("--intro-hud", "1");
    intro.style.setProperty("--intro-actions", "1");
    intro.style.setProperty("--intro-exit", "0");
    intro.style.setProperty("--intro-dark", "0.82");
    intro.style.setProperty("--intro-video-brightness", "1");
    intro.style.setProperty("--intro-mobile-video-brightness", "0.96");
    intro.style.setProperty("--intro-video-opacity", "0.96");
    intro.style.setProperty("--intro-video-scale", "1.03");
    intro.style.setProperty("--intro-shade-mid", "0.32");
    intro.style.setProperty("--intro-vignette-bottom", "0.28");
    intro.style.setProperty("--intro-scan-opacity", "0.36");
    intro.style.setProperty("--intro-scan-y", "100%");
    intro.style.setProperty("--intro-frame-opacity", "0.13");
    intro.style.setProperty("--intro-frame-blue-opacity", "0.18");
    intro.style.setProperty("--intro-minimal-opacity", "0.2");
    intro.style.setProperty("--intro-fleet-opacity", "0.18");
    intro.style.setProperty("--intro-mobile-fleet-opacity", "0.16");
    intro.style.setProperty("--intro-fleet-y", "0px");
    intro.style.setProperty("--intro-fleet-scale", "1");
    intro.style.setProperty("--intro-title-clip", "0%");
    intro.style.setProperty("--intro-title-y", "0px");
    intro.style.setProperty("--intro-motto-y", "0px");
    intro.style.setProperty("--intro-motto-clip", "0%");
    intro.style.setProperty("--intro-hud-left-x", "0px");
    intro.style.setProperty("--intro-hud-right-x", "0px");
    intro.style.setProperty("--intro-actions-y", "0px");
    intro.style.setProperty("--intro-actions-line-x", "0%");
    intro.style.setProperty("--intro-cue-y", "0px");
    root.style.setProperty("--command-nav-opacity", "1");
    root.style.setProperty("--command-nav-y", "0px");
    root.style.setProperty("--command-nav-pointer", "auto");
    root.style.setProperty("--hero-progress", "1");
    return;
  }

  const rect = intro.getBoundingClientRect();
  const scrollable = Math.max(1, rect.height - window.innerHeight);
  const progress = clamp((0 - rect.top) / scrollable, 0, 1);
  const title = smoothRange(progress, 0.15, 0.35) * (1 - smoothRange(progress, 0.9, 1));
  const motto = smoothRange(progress, 0.35, 0.55) * (1 - smoothRange(progress, 0.88, 1));
  const hud = smoothRange(progress, 0.55, 0.75);
  const actions = smoothRange(progress, 0.75, 0.98);
  const exit = smoothRange(progress, 0.88, 1);
  const navReveal = smoothRange(progress, 0.58, 0.76);
  const dark = clamp(0.28 + motto * 0.12 + hud * 0.08 + exit * 0.22, 0.28, 0.7);
  const videoBrightness = clamp(1 - exit * 0.16, 0.82, 1);
  const mobileVideoBrightness = clamp(0.96 - exit * 0.12, 0.78, 0.96);
  const videoOpacity = clamp(0.96 - exit * 0.16, 0.78, 0.96);
  const videoScale = 1.03 + progress * 0.035;
  const scanY = -26 + progress * 520;
  const scanOpacity = clamp(0.16 + title * 0.18 + actions * 0.12, 0.12, 0.46);
  const fleetOpacity = clamp(0.06 + hud * 0.15 - exit * 0.08, 0.03, 0.21);
  const mobileFleetOpacity = clamp(0.04 + hud * 0.12 - exit * 0.05, 0.02, 0.16);

  intro.style.setProperty("--intro-progress", progress.toFixed(4));
  intro.style.setProperty("--intro-title", title.toFixed(4));
  intro.style.setProperty("--intro-motto", motto.toFixed(4));
  intro.style.setProperty("--intro-hud", hud.toFixed(4));
  intro.style.setProperty("--intro-actions", actions.toFixed(4));
  intro.style.setProperty("--intro-exit", exit.toFixed(4));
  intro.style.setProperty("--intro-dark", dark.toFixed(4));
  intro.style.setProperty("--intro-video-brightness", videoBrightness.toFixed(4));
  intro.style.setProperty("--intro-mobile-video-brightness", mobileVideoBrightness.toFixed(4));
  intro.style.setProperty("--intro-video-opacity", videoOpacity.toFixed(4));
  intro.style.setProperty("--intro-video-scale", videoScale.toFixed(4));
  intro.style.setProperty("--intro-shade-mid", clamp(0.22 + dark * 0.32, 0.22, 0.46).toFixed(4));
  intro.style.setProperty("--intro-vignette-bottom", clamp(0.26 + exit * 0.24, 0.26, 0.5).toFixed(4));
  intro.style.setProperty("--intro-scan-opacity", scanOpacity.toFixed(4));
  intro.style.setProperty("--intro-scan-y", `${scanY.toFixed(2)}%`);
  intro.style.setProperty("--intro-frame-opacity", clamp(0.05 + hud * 0.08, 0.05, 0.13).toFixed(4));
  intro.style.setProperty("--intro-frame-blue-opacity", clamp(0.06 + hud * 0.12, 0.06, 0.18).toFixed(4));
  intro.style.setProperty("--intro-minimal-opacity", clamp(0.42 - title * 0.16, 0.18, 0.42).toFixed(4));
  intro.style.setProperty("--intro-fleet-opacity", fleetOpacity.toFixed(4));
  intro.style.setProperty("--intro-mobile-fleet-opacity", mobileFleetOpacity.toFixed(4));
  intro.style.setProperty("--intro-fleet-y", `${(-exit * 34).toFixed(2)}px`);
  intro.style.setProperty("--intro-fleet-scale", (1 + progress * 0.06).toFixed(4));
  intro.style.setProperty("--intro-title-clip", `${((1 - title) * 100).toFixed(2)}%`);
  intro.style.setProperty("--intro-title-y", `${((1 - title) * 24 - exit * 44).toFixed(2)}px`);
  intro.style.setProperty("--intro-motto-y", `${((1 - motto) * 22 - exit * 38).toFixed(2)}px`);
  intro.style.setProperty("--intro-motto-clip", `${((1 - motto) * 100).toFixed(2)}%`);
  intro.style.setProperty("--intro-hud-left-x", `${((1 - hud) * -34).toFixed(2)}px`);
  intro.style.setProperty("--intro-hud-right-x", `${((1 - hud) * 34).toFixed(2)}px`);
  intro.style.setProperty("--intro-actions-y", `${((1 - actions) * 20).toFixed(2)}px`);
  intro.style.setProperty("--intro-actions-line-x", `${(-100 + actions * 100).toFixed(2)}%`);
  intro.style.setProperty("--intro-cue-y", `${((1 - actions) * 12).toFixed(2)}px`);
  root.style.setProperty("--command-nav-opacity", navReveal.toFixed(4));
  root.style.setProperty("--command-nav-y", `${((1 - navReveal) * -12).toFixed(2)}px`);
  root.style.setProperty("--command-nav-pointer", navReveal > 0.95 ? "auto" : "none");
  root.style.setProperty("--hero-progress", progress.toFixed(4));
}

function initPointerParallax() {
  if (prefersReducedMotion) return;

  window.addEventListener(
    "pointermove",
    (event) => {
      const x = clamp((event.clientX / window.innerWidth - 0.5) * 10, -5, 5);
      const y = clamp((event.clientY / window.innerHeight - 0.5) * 10, -5, 5);
      root.style.setProperty("--pointer-x", `${x.toFixed(2)}px`);
      root.style.setProperty("--pointer-y", `${y.toFixed(2)}px`);
    },
    { passive: true },
  );
}

function initSmoothLinks() {
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const target = document.querySelector(link.getAttribute("href"));
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: prefersReducedMotion ? "auto" : "smooth", block: "start" });
    });
  });
}

function initNavSpy() {
  const targetMap = new Map();
  navLinks.forEach((link) => {
    const href = link.getAttribute("href");
    if (!href?.startsWith("#") || targetMap.has(href)) return;
    const section = document.querySelector(href);
    if (section) targetMap.set(href, { href, section, links: [] });
  });

  navLinks.forEach((link) => {
    const href = link.getAttribute("href");
    targetMap.get(href)?.links.push(link);
  });

  const targets = [...targetMap.values()]
    .map((link) => {
      return link;
    })
    .filter(Boolean);
  if (!targets.length) return;

  let ticking = false;

  function sync() {
    const viewportTop = Number.parseFloat(getComputedStyle(root).getPropertyValue("--nav-h")) || 74;
    const viewportBottom = window.innerHeight;
    let active = null;
    let bestScore = -1;

    targets.forEach((item) => {
      const rect = item.section.getBoundingClientRect();
      const visibleTop = Math.max(rect.top, viewportTop);
      const visibleBottom = Math.min(rect.bottom, viewportBottom);
      const visibleHeight = Math.max(0, visibleBottom - visibleTop);
      const centerDistance = Math.abs((rect.top + rect.bottom) / 2 - window.innerHeight * 0.5);
      const score = visibleHeight * 2 - centerDistance * 0.18;
      if (score > bestScore) {
        bestScore = score;
        active = item;
      }
    });

    if (bestScore <= 0 && window.scrollY < targets[0].section.offsetTop - window.innerHeight * 0.5) {
      active = null;
    } else if (!active || bestScore <= 0) {
      active = targets[0];
    }

    const nearBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 24;
    if (nearBottom) active = targets[targets.length - 1];

    targets.forEach((item) => {
      item.links.forEach((link) => {
        link.classList.toggle("is-active", item === active);
        if (item === active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    });
  }

  function requestSync() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      sync();
      ticking = false;
    });
  }

  sync();
  window.addEventListener("scroll", requestSync, { passive: true });
  window.addEventListener("resize", requestSync, { passive: true });
}

function initReveal() {
  const items = [...document.querySelectorAll(".reveal")];
  if (!items.length) return;

  if (prefersReducedMotion) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -12% 0px", threshold: 0.16 },
  );
  items.forEach((item) => observer.observe(item));
}

function initDoctrinePanel() {
  const items = [...document.querySelectorAll("[data-doctrine]")];
  const nodes = [...document.querySelectorAll("[data-node]")];
  if (!items.length) return;

  function activate(key) {
    items.forEach((item) => item.classList.toggle("active", item.dataset.doctrine === key));
    nodes.forEach((node) => node.classList.toggle("active", node.dataset.node === key));
  }

  items.forEach((item) => {
    const key = item.dataset.doctrine;
    item.addEventListener("mouseenter", () => activate(key));
    item.addEventListener("focus", () => activate(key));
  });
}

function initOperationMap() {
  const map = document.querySelector("[data-operation-map]");
  const filters = [...document.querySelectorAll("[data-filter]")];
  const nodes = [...document.querySelectorAll(".operation-node")];
  if (!filters.length || !nodes.length) return;

  function activateNode(node, interacting = true) {
    if (!node) return;
    const role = node.dataset.role || "combat";
    nodes.forEach((item) => item.classList.toggle("active", item === node));
    map?.setAttribute("data-active-role", role);
    map?.classList.toggle("is-interacting", interacting);
  }

  function setFilter(role) {
    filters.forEach((button) => button.classList.toggle("active", button.dataset.filter === role));
    nodes.forEach((node) => {
      const matches = role === "all" || node.dataset.role === role;
      node.classList.toggle("is-dimmed", !matches);
    });
    const activeNode = role === "all" ? nodes[0] : nodes.find((node) => node.dataset.role === role);
    activateNode(activeNode, role !== "all");
  }

  filters.forEach((button) => {
    button.addEventListener("click", () => setFilter(button.dataset.filter));
  });

  nodes.forEach((node) => {
    node.addEventListener("mouseenter", () => {
      activateNode(node, true);
    });
    node.addEventListener("focus", () => {
      activateNode(node, true);
    });
  });

  map?.addEventListener("mouseleave", () => {
    activateNode(nodes[0], false);
  });

  activateNode(nodes.find((node) => node.classList.contains("active")) || nodes[0], false);
}

function initApplicationForm() {
  const form = document.querySelector("#applicationForm");
  const output = document.querySelector("#applicationOutput");
  const copyButton = document.querySelector("[data-copy-card]");
  if (!form || !output) return;

  function buildCard() {
    const formData = new FormData(form);
    const gameId = String(formData.get("gameId") || "").trim();
    const role = String(formData.get("role") || "探索侦察");

    if (!gameId) {
      output.textContent = "填写游戏 ID 后，生成一段可复制的申请卡文案。\n真实加入舰队仍需要前往 RSI 官网 GVY 页面提交申请。";
      return false;
    }

    output.textContent = `我是 ${gameId}，希望加入星际远航者舰队。
偏好位置：${role}
我认同舰队“勇敢追寻，无限探索”的理念，希望和大家一起远航、协作、探索未知。`;
    return true;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    buildCard();
  });

  form.addEventListener("input", () => {
    const field = form.elements.gameId;
    if (field?.value?.trim()) buildCard();
  });

  copyButton?.addEventListener("click", async () => {
    if (!buildCard()) return;
    const text = output.textContent.trim();
    try {
      await navigator.clipboard.writeText(text);
      copyButton.textContent = "已复制";
      setTimeout(() => {
        copyButton.textContent = "复制申请卡";
      }, 1400);
    } catch {
      copyButton.textContent = "请手动选择复制";
      setTimeout(() => {
        copyButton.textContent = "复制申请卡";
      }, 1800);
    }
  });
}

function initArchiveLightbox() {
  const dialog = document.querySelector("#archiveDialog");
  const image = document.querySelector("#archiveDialogImage");
  const caption = document.querySelector("#archiveDialogCaption");
  const frames = [...document.querySelectorAll(".archive-frame[data-full]")];
  if (!dialog || !image || !caption || !frames.length) return;

  frames.forEach((frame) => {
    frame.addEventListener("click", () => {
      const src = frame.dataset.full;
      const label = frame.dataset.caption || frame.querySelector("img")?.alt || "GVY ARCHIVE";
      if (!src) return;
      image.src = src;
      image.alt = label;
      caption.textContent = `GVY ARCHIVE / FLEET MEMORY / ${label}`;
      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        window.open(src, "_blank", "noopener,noreferrer");
      }
    });
  });

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  dialog.addEventListener("close", () => {
    image.removeAttribute("src");
  });
}

function initArchiveImageFallback() {
  const frames = [...document.querySelectorAll(".archive-frame[data-full]")];
  frames.forEach((frame) => {
    const image = frame.querySelector("img");
    if (!image) return;

    function handleImageError() {
      if (image.dataset.fallbackTried !== "true") {
        image.dataset.fallbackTried = "true";
        image.src = frame.dataset.full;
        return;
      }

      frame.classList.add("is-image-missing");
      image.hidden = true;
    }

    image.addEventListener("error", handleImageError);
    if (image.complete && image.naturalWidth === 0) handleImageError();
  });
}

function initArchiveOrbit() {
  const gallery = document.querySelector("[data-orbit-gallery]");
  const frames = [...document.querySelectorAll("[data-orbit-gallery] .archive-frame")];
  if (!gallery || !frames.length) return;

  let frameId = 0;
  let active = false;
  let paused = false;
  let orbitStartTime = 0;
  let pausedAt = 0;
  let pausedDuration = 0;
  let lastTickTime = 0;
  let size = { width: 0, height: 0, radiusX: 0, radiusY: 0, radiusZ: 0 };
  const orbitItems = frames.map((frame, index) => ({
    frame,
    angle: (index / frames.length) * Math.PI * 2,
    zIndex: "",
    pointerEvents: "",
  }));

  function measure() {
    const box = gallery.getBoundingClientRect();
    size = {
      width: box.width,
      height: box.height,
      radiusX: clamp(box.width * 0.34, 210, 560),
      radiusY: clamp(box.height * 0.13, 62, 132),
      radiusZ: clamp(box.width * 0.24, 160, 390),
    };
    if (window.innerWidth < 720) {
      size.radiusX = clamp(box.width * 0.28, 130, 230);
      size.radiusY = clamp(box.height * 0.11, 44, 88);
      size.radiusZ = clamp(box.width * 0.18, 90, 170);
    }
  }

  function getOrbitTime(time) {
    if (!orbitStartTime && time > 0) orbitStartTime = time;
    if (!orbitStartTime) return 0;
    return Math.max(0, time - orbitStartTime - pausedDuration);
  }

  function place(time = lastTickTime) {
    const rotation = prefersReducedMotion ? 0.72 : getOrbitTime(time) * 0.000105;
    orbitItems.forEach((item, index) => {
      const { frame } = item;
      const angle = item.angle + rotation;
      const x = Math.sin(angle) * size.radiusX;
      const depth = Math.cos(angle);
      const depth01 = (depth + 1) / 2;
      const y = Math.sin(angle * 1.7 + index * 0.48) * size.radiusY;
      const scale = 0.58 + depth01 * 0.48;
      const opacity = 0.26 + depth01 * 0.7;
      const zIndex = String(Math.round(8 + depth01 * 18));
      const tilt = -Math.sin(angle) * 5;
      const pointerEvents = depth01 > 0.18 ? "auto" : "none";

      if (item.zIndex !== zIndex) {
        frame.style.zIndex = zIndex;
        item.zIndex = zIndex;
      }
      frame.style.opacity = opacity.toFixed(3);
      frame.style.transform = `translate(-50%, -50%) translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0) rotateY(${tilt.toFixed(2)}deg) scale(${scale.toFixed(3)})`;
      if (item.pointerEvents !== pointerEvents) {
        frame.style.pointerEvents = pointerEvents;
        item.pointerEvents = pointerEvents;
      }

      if (prefersReducedMotion) {
        frame.style.setProperty("--static-x", `${x.toFixed(1)}px`);
        frame.style.setProperty("--static-y", `${y.toFixed(1)}px`);
        frame.style.setProperty("--static-scale", scale.toFixed(3));
      }
    });
  }

  function tick(time) {
    if (!active || paused || prefersReducedMotion) return;
    lastTickTime = time;
    place(time);
    frameId = requestAnimationFrame(tick);
  }

  function start() {
    if (active && !paused) return;
    active = true;
    paused = false;
    pausedAt = 0;
    cancelAnimationFrame(frameId);
    frameId = requestAnimationFrame(tick);
  }

  function stop() {
    active = false;
    paused = false;
    pausedAt = 0;
    cancelAnimationFrame(frameId);
  }

  measure();
  place(0);

  frames.forEach((frame) => {
    frame.addEventListener("mouseenter", () => {
      if (paused) return;
      paused = true;
      pausedAt = performance.now();
      cancelAnimationFrame(frameId);
    });
    frame.addEventListener("mouseleave", () => {
      if (!active || prefersReducedMotion) return;
      if (!paused) return;
      if (pausedAt) {
        pausedDuration += performance.now() - pausedAt;
        pausedAt = 0;
      }
      paused = false;
      frameId = requestAnimationFrame(tick);
    });
  });

  const observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      if (entry?.isIntersecting) start();
      else stop();
    },
    { threshold: 0.12 },
  );
  observer.observe(gallery);

  window.addEventListener(
    "resize",
    () => {
      measure();
      place(lastTickTime);
    },
    { passive: true },
  );
}

function initScrollLoop() {
  let ticking = false;

  function requestUpdate() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      updateIntroProgress();
      ticking = false;
    });
  }

  updateIntroProgress();
  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", requestUpdate, { passive: true });
}

initStarfield();
initPointerParallax();
initScrollLoop();
initSmoothLinks();
initNavSpy();
initReveal();
initDoctrinePanel();
initOperationMap();
initArchiveImageFallback();
initArchiveOrbit();
initApplicationForm();
initArchiveLightbox();
