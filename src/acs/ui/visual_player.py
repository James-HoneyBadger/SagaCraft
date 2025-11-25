#!/usr/bin/env python3
"""Lightweight point-and-click helper window for visual adventures."""

from __future__ import annotations

import tkinter as tk
from functools import partial
from tkinter import ttk
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence


class PointAndClickWindow:
    """Render adventure scenes with clickable hotspots that trigger commands."""

    def __init__(
        self,
        root: tk.Tk,
        scenes: Sequence[Dict[str, Any]],
        *,
        command_callback: Callable[[str | List[str]], None],
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        self.root = root
        self.command_callback = command_callback
        self.on_close = on_close

        self.window = tk.Toplevel(root)
        self.window.title("Point & Click View")
        self.window.geometry("960x640")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        controls = ttk.Frame(self.window)
        controls.pack(fill=tk.X)

        self._hotspots_visible = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls,
            text="Show Hotspots",
            variable=self._hotspots_visible,
            command=self._update_hotspot_visibility,
        ).pack(side=tk.LEFT, padx=(10, 6), pady=6)

        self._grid_visible = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls,
            text="Grid Overlay",
            variable=self._grid_visible,
            command=self._apply_grid_overlay,
        ).pack(side=tk.LEFT, padx=6, pady=6)

        self.canvas = tk.Canvas(self.window, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        status_bar = ttk.Frame(self.window)
        status_bar.pack(fill=tk.X)
        self._idle_status = "Select a hotspot to send a command."
        self.status_var = tk.StringVar(value=self._idle_status)
        self._status_reset_job: Optional[str] = None
        ttk.Label(status_bar, textvariable=self.status_var).pack(
            side=tk.LEFT, padx=10, pady=4
        )

        self._image_cache: Dict[str, tk.PhotoImage] = {}
        self._current_image_key: Optional[str] = None
        self.current_scene_id: Optional[int] = None
        self.current_scene: Optional[Dict[str, Any]] = None
        self.hotspot_items: List[int] = []
        self._grid_items: List[int] = []
        self._grid_step = 64
        self._background_dimensions: tuple[int, int] = (960, 640)
        self._hotspot_metadata: Dict[int, Dict[str, Any]] = {}
        self._hover_info: Optional[Dict[str, Any]] = None
        self._hover_text_id: Optional[int] = None
        self._hover_text_bg_id: Optional[int] = None

        self.scenes: List[Dict[str, Any]] = []
        self._scenes_by_room: Dict[int, Dict[str, Any]] = {}
        self.update_scenes(scenes)

    # ------------------------------------------------------------------
    # Scene management
    # ------------------------------------------------------------------

    def update_scenes(self, scenes: Sequence[Dict[str, Any]]) -> None:
        """Store scenes and build quick lookup tables."""
        self.scenes = list(scenes)
        self._scenes_by_room.clear()
        for scene in self.scenes:
            room_id = scene.get("room_id")
            if room_id is not None:
                try:
                    self._scenes_by_room[int(room_id)] = scene
                except (TypeError, ValueError):
                    continue

    def set_current_room(self, room_id: Optional[int]) -> None:
        """Display the scene associated with the given room."""
        target_scene: Optional[Dict[str, Any]] = None
        if room_id is not None:
            target_scene = self._scenes_by_room.get(int(room_id))

        if target_scene is None and self.scenes:
            target_scene = self.scenes[0]

        if target_scene is None:
            self._show_blank(message="No visual scene available for this room.")
            return

        self._display_scene(target_scene)

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _display_scene(self, scene: Dict[str, Any]) -> None:
        scene_id = scene.get("id")
        background = scene.get("background", "")
        image = self._load_image(background)

        self._clear_hotspot_highlight()
        self.canvas.delete("all")
        self.hotspot_items.clear()
        self._hotspot_metadata.clear()
        width: int
        height: int
        if image is not None:
            width = image.width()
            height = image.height()
            self.canvas.config(scrollregion=(0, 0, width, height))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image, tags=("scene",))
            self._current_image_key = str(background)
        else:
            width = 960
            height = 640
            self.canvas.config(scrollregion=(0, 0, width, height))
            self.canvas.create_rectangle(
                0,
                0,
                width,
                height,
                fill="#1f1f1f",
                outline="#2a2a2a",
            )
            self.canvas.create_text(
                width / 2,
                height / 2,
                text="[Missing Background]\n" + str(background),
                fill="#cccccc",
                font=("Segoe UI", 16, "italic"),
                justify=tk.CENTER,
            )
            self._current_image_key = None

        self._background_dimensions = (width, height)
        try:
            step_value = int(scene.get("grid_size", 64))
        except (TypeError, ValueError):
            step_value = 64
        self._grid_step = max(16, min(256, step_value))

        grid_setting = scene.get("grid_visible")
        if grid_setting is None:
            self._grid_visible.set(False)
        else:
            self._grid_visible.set(bool(grid_setting))

        self._apply_grid_overlay(width, height)

        self.current_scene_id = scene_id
        self.current_scene = scene

        narration = scene.get("narration")
        if narration:
            self._set_idle_status(str(narration))
        else:
            self._set_idle_status("Click a hotspot to send a command.")

        self._draw_hotspots(scene.get("hotspots", []) or [])

    def _draw_hotspots(self, hotspots: Sequence[Dict[str, Any]]) -> None:
        self._hotspot_metadata.clear()
        for index, hotspot in enumerate(hotspots):
            try:
                x = int(hotspot.get("x", 0))
                y = int(hotspot.get("y", 0))
                width = int(hotspot.get("width", 100))
                height = int(hotspot.get("height", 100))
            except (TypeError, ValueError):
                continue

            rect_id = self.canvas.create_rectangle(
                x,
                y,
                x + width,
                y + height,
                outline="#58a6ff",
                width=2,
                fill="#58a6ff",
                stipple="gray25",
                tags=("hotspot", f"hotspot-{index}"),
            )
            label = hotspot.get("label", "Hotspot")
            text_id = self.canvas.create_text(
                x + width / 2,
                y + 12,
                text=label,
                fill="#58a6ff",
                font=("Segoe UI", 10, "bold"),
                tags=("hotspot", f"hotspot-label-{index}"),
            )
            info = {"data": hotspot, "rect_id": rect_id, "label_id": text_id}
            self._hotspot_metadata[rect_id] = info
            self._hotspot_metadata[text_id] = info
            for item_id in (rect_id, text_id):
                self.canvas.tag_bind(
                    item_id,
                    "<Enter>",
                    partial(self._on_hotspot_enter, info=info),
                )
                self.canvas.tag_bind(
                    item_id,
                    "<Leave>",
                    partial(self._on_hotspot_leave, info=info),
                )
                self.canvas.tag_bind(
                    item_id,
                    "<Motion>",
                    partial(self._on_hotspot_motion, info=info),
                )
                self.canvas.tag_bind(
                    item_id,
                    "<Button-1>",
                    partial(self._on_hotspot_click, info=info),
                )
            self.hotspot_items.extend([rect_id, text_id])
        self.canvas.tag_raise("hotspot")
        self._update_hotspot_visibility()

    # ------------------------------------------------------------------
    # Overlay & status helpers
    # ------------------------------------------------------------------

    def _apply_hotspot_style(self, rect_id: int, *, active: bool) -> None:
        try:
            if active:
                self.canvas.itemconfigure(
                    rect_id,
                    outline="#f8f9ff",
                    width=3,
                    fill="#7fb3ff",
                    stipple="gray12",
                )
            else:
                self.canvas.itemconfigure(
                    rect_id,
                    outline="#58a6ff",
                    width=2,
                    fill="#58a6ff",
                    stipple="gray25",
                )
        except tk.TclError:
            return

    def _clear_hotspot_highlight(self) -> None:
        if self._hover_info is not None:
            rect_id = self._hover_info.get("rect_id")
            if rect_id is not None:
                self._apply_hotspot_style(rect_id, active=False)
        self._hover_info = None
        self._hide_hotspot_hint()
        self.canvas.config(cursor="")

    def _show_hotspot_hint(self, x: int, y: int, text: str) -> None:
        offset_x = 12
        offset_y = 18
        target_y = max(0, y - offset_y)
        if self._hover_text_id is None:
            try:
                self._hover_text_id = self.canvas.create_text(
                    x + offset_x,
                    target_y,
                    text=text,
                    anchor=tk.NW,
                    fill="#f5faff",
                    font=("Segoe UI", 10, "bold"),
                    tags=("hotspot-hint",),
                )
            except tk.TclError:
                self._hover_text_id = None
                return
        else:
            try:
                self.canvas.itemconfigure(self._hover_text_id, text=text)
                self.canvas.coords(self._hover_text_id, x + offset_x, target_y)
            except tk.TclError:
                return

        bbox = self.canvas.bbox(self._hover_text_id)
        if bbox is None:
            return

        if self._hover_text_bg_id is None:
            try:
                self._hover_text_bg_id = self.canvas.create_rectangle(
                    bbox[0] - 4,
                    bbox[1] - 2,
                    bbox[2] + 4,
                    bbox[3] + 2,
                    fill="#050505",
                    outline="#0f111a",
                    width=1,
                    tags=("hotspot-hint",),
                )
            except tk.TclError:
                self._hover_text_bg_id = None
                return
        else:
            try:
                self.canvas.coords(
                    self._hover_text_bg_id,
                    bbox[0] - 4,
                    bbox[1] - 2,
                    bbox[2] + 4,
                    bbox[3] + 2,
                )
            except tk.TclError:
                return

        try:
            if self._hover_text_bg_id is not None:
                self.canvas.tag_lower(self._hover_text_bg_id, self._hover_text_id)
            if self._hover_text_id is not None:
                self.canvas.tag_raise(self._hover_text_id)
        except tk.TclError:
            return

    def _hide_hotspot_hint(self) -> None:
        if self._hover_text_id is not None:
            try:
                self.canvas.delete(self._hover_text_id)
            except tk.TclError:
                pass
            finally:
                self._hover_text_id = None
        if self._hover_text_bg_id is not None:
            try:
                self.canvas.delete(self._hover_text_bg_id)
            except tk.TclError:
                pass
            finally:
                self._hover_text_bg_id = None

    def _update_hotspot_visibility(self) -> None:
        state = tk.NORMAL if self._hotspots_visible.get() else tk.HIDDEN
        for item_id in self.hotspot_items:
            try:
                self.canvas.itemconfigure(item_id, state=state)
            except tk.TclError:
                continue
        if not self._hotspots_visible.get():
            self._clear_hotspot_highlight()
        else:
            try:
                self.canvas.tag_raise("hotspot")
            except tk.TclError:
                pass

    def _apply_grid_overlay(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        if width is None or height is None:
            width, height = self._background_dimensions
        self._clear_grid()
        if not self._grid_visible.get():
            return
        step = max(16, self._grid_step)
        try:
            for x in range(step, width, step):
                self._grid_items.append(
                    self.canvas.create_line(
                        x,
                        0,
                        x,
                        height,
                        fill="#1a4c7c",
                        dash=(2, 6),
                        width=1,
                        tags=("grid",),
                    )
                )
            for y in range(step, height, step):
                self._grid_items.append(
                    self.canvas.create_line(
                        0,
                        y,
                        width,
                        y,
                        fill="#1a4c7c",
                        dash=(2, 6),
                        width=1,
                        tags=("grid",),
                    )
                )
        except tk.TclError:
            self._clear_grid()
            return
        try:
            self.canvas.tag_raise("grid", "scene")
        except tk.TclError:
            pass
        try:
            self.canvas.tag_lower("grid", "hotspot")
        except tk.TclError:
            pass

    def _clear_grid(self) -> None:
        while self._grid_items:
            item_id = self._grid_items.pop()
            try:
                self.canvas.delete(item_id)
            except tk.TclError:
                continue

    def _set_status(
        self, message: str, *, temporary: bool = False, delay: int = 1500
    ) -> None:
        self._cancel_status_reset()
        self.status_var.set(message)
        if temporary:
            self._status_reset_job = self.window.after(delay, self._restore_idle_status)

    def _set_idle_status(self, message: str) -> None:
        self._idle_status = message
        self._set_status(message)

    def _restore_idle_status(self) -> None:
        self._status_reset_job = None
        self.status_var.set(self._idle_status)

    def _cancel_status_reset(self) -> None:
        if self._status_reset_job is not None:
            try:
                self.window.after_cancel(self._status_reset_job)
            except tk.TclError:
                pass
            finally:
                self._status_reset_job = None

    def _on_hotspot_enter(self, event: tk.Event, *, info: Dict[str, Any]) -> None:
        rect_id = info.get("rect_id")
        if rect_id is None:
            return
        self._hover_info = info
        self._apply_hotspot_style(rect_id, active=True)
        label_id = info.get("label_id")
        if label_id is not None:
            try:
                self.canvas.tag_raise(label_id)
            except tk.TclError:
                pass
        try:
            self.canvas.tag_raise(rect_id)
        except tk.TclError:
            pass
        tooltip = info["data"].get("tooltip") or info["data"].get("label") or "Hotspot"
        text = str(tooltip)
        self._set_status(text)
        self.canvas.config(cursor="hand2")
        self._show_hotspot_hint(event.x, event.y, text)

    def _on_hotspot_leave(self, _event: tk.Event, *, info: Dict[str, Any]) -> None:
        rect_id = info.get("rect_id")
        if rect_id is not None:
            self._apply_hotspot_style(rect_id, active=False)
        if self._hover_info is info:
            self._hover_info = None
        self._hide_hotspot_hint()
        self.canvas.config(cursor="")
        self._restore_idle_status()

    def _on_hotspot_motion(self, event: tk.Event, *, info: Dict[str, Any]) -> None:
        if self._hover_info is not info:
            return
        tooltip = info["data"].get("tooltip") or info["data"].get("label") or "Hotspot"
        self._show_hotspot_hint(event.x, event.y, str(tooltip))

    def _on_hotspot_click(self, _event: tk.Event, *, info: Dict[str, Any]) -> None:
        self._handle_hotspot(info["data"])

    def _show_blank(self, *, message: str = "") -> None:
        self._clear_hotspot_highlight()
        self.canvas.delete("all")
        self.hotspot_items.clear()
        self._hotspot_metadata.clear()
        width, height = 960, 640
        self._background_dimensions = (width, height)
        self.canvas.config(scrollregion=(0, 0, width, height))
        self.canvas.create_rectangle(
            0,
            0,
            width,
            height,
            fill="#1f1f1f",
            outline="#2a2a2a",
        )
        if message:
            self.canvas.create_text(
                width / 2,
                height / 2,
                text=message,
                fill="#cccccc",
                font=("Segoe UI", 16, "italic"),
                justify=tk.CENTER,
            )
        self._apply_grid_overlay(width, height)
        self._set_idle_status(message or "No scene to display.")

    def _load_image(self, path_value: Any) -> Optional[tk.PhotoImage]:
        if not path_value:
            return None
        path = Path(str(path_value)).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        key = str(path)
        if key in self._image_cache:
            return self._image_cache[key]
        if not path.exists():
            return None
        try:
            image = tk.PhotoImage(file=key)
        except tk.TclError:
            return None
        self._image_cache[key] = image
        return image

    # ------------------------------------------------------------------
    # Interaction handling
    # ------------------------------------------------------------------

    def _handle_hotspot(self, hotspot: Dict[str, Any]) -> None:
        action = hotspot.get("action", "command")
        value = hotspot.get("value", "")
        if not value:
            self._set_status("Hotspot has no command to execute.", temporary=True)
            return

        if action == "command_sequence":
            commands = [part.strip() for part in value.split(";") if part.strip()]
            payload: str | List[str] = commands
        else:
            payload = value.strip()

        self._set_status(f"Running {action}...")
        self.command_callback(payload)
        self._set_status("Command sent.", temporary=True)

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Destroy the window and reset callbacks."""
        self.destroy()
        if self.on_close:
            self.on_close()

    def destroy(self) -> None:
        """Destroy the toplevel if it still exists."""
        if self.window.winfo_exists():
            self.window.destroy()
