"""Generate the Precision Auto Clicker app icon.

The mark combines the two ideas in the product name and behaviour:
  * a precision crosshair / target  -> "Precision"
  * a mouse cursor with click-ripple rings -> "Auto Clicker" (repeated clicks)

It is drawn at high resolution and downsampled so the small title-bar and
taskbar sizes stay crisp. Run this to regenerate assets/app_icon.{ico,png}.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

# Palette pulled straight from the app UI (ui.py).
BLUE_LIGHT = (9, 105, 218)     # #0969da  primary accent
BLUE_DARK = (6, 79, 159)       # #064f9f  pressed/active accent
WHITE = (255, 255, 255)

MASTER = 1024                  # render size for the standalone PNG
SUPERSAMPLE = 4                # per-size oversampling for crisp edges
# Includes the in-between sizes Windows requests at 125% / 150% / 175% DPI
# (20, 24, 40) so the taskbar never has to rescale a mismatched frame.
ICO_SIZES = [256, 128, 64, 48, 40, 32, 24, 20, 16]


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _vertical_gradient(size: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    grad = Image.new("RGB", (1, size))
    for y in range(size):
        grad.putpixel((0, y), _lerp(top, bottom, y / (size - 1)))
    return grad.resize((size, size))


def _rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def _ring(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, width: float,
          fill: tuple[int, int, int, int]) -> None:
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=round(width))


# Per-tier ripple geometry. Smaller icons get fewer, bolder, more opaque rings
# and a larger cursor so the mark stays crisp and high-contrast instead of
# smearing into a hazy blob. (r, alpha, width) as fractions of the tile.
RIPPLE_TIERS = {
    "full": {  # >= 48px: the detailed three-ring mark
        "center": (0.42, 0.40),
        "rings": ((0.42, 80, 0.024), (0.32, 150, 0.030), (0.22, 220, 0.038)),
        "cursor": 0.0034,
        "outline": 0.006,
        "shadow": True,
    },
    "mid": {  # 24-32px: two bold, near-opaque rings, bigger cursor
        "center": (0.37, 0.32),
        "rings": ((0.40, 200, 0.052), (0.265, 255, 0.064)),
        "cursor": 0.0039,
        "outline": 0.0,
        "shadow": False,
    },
    "small": {  # <= 20px: one bold ring + a dominant cursor silhouette
        "center": (0.36, 0.30),
        "rings": ((0.33, 255, 0.090),),
        "cursor": 0.0041,
        "outline": 0.0,
        "shadow": False,
    },
}


def build_master(variant: str = "ripple", size: int = MASTER, tier: str = "full") -> Image.Image:
    s = size
    # Rounded-square app tile with a subtle vertical blue gradient.
    tile = _vertical_gradient(s, _lerp(BLUE_LIGHT, (40, 130, 230), 0.0), BLUE_DARK).convert("RGBA")
    tile.putalpha(_rounded_mask(s, radius=round(s * 0.22)))

    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    if variant == "target":
        cx, cy = s * 0.42, s * 0.40
        for r, alpha, w in ((s * 0.38, 80, s * 0.024), (s * 0.29, 150, s * 0.030)):
            _ring(d, cx, cy, r, w, (*WHITE, alpha))
        tick_in, tick_out = s * 0.16, s * 0.225
        tw = s * 0.030
        cross = (*WHITE, 210)
        d.line([cx, cy - tick_out, cx, cy - tick_in], fill=cross, width=round(tw))
        d.line([cx, cy + tick_in, cx, cy + tick_out], fill=cross, width=round(tw))
        d.line([cx - tick_out, cy, cx - tick_in, cy], fill=cross, width=round(tw))
        d.line([cx + tick_in, cy, cx + tick_out, cy], fill=cross, width=round(tw))
        spec = RIPPLE_TIERS["full"]
    else:
        # Graduated click-ripple rings radiating from the click point: the
        # cursor "pulses" repeated clicks outward (auto-clicking).
        spec = RIPPLE_TIERS[tier]
        cx, cy = s * spec["center"][0], s * spec["center"][1]
        for r, alpha, w in spec["rings"]:
            _ring(d, cx, cy, s * r, s * w, (*WHITE, alpha))

    # Classic arrow cursor, tip anchored at the click point, body down-right.
    tip = (cx, cy)
    scale = s * spec["cursor"]
    # Local cursor outline (tip at 0,0, pointing up-left).
    pts_local = [
        (0, 0), (0, 132), (33, 100), (58, 158),
        (82, 148), (58, 92), (98, 92),
    ]
    pts = [(tip[0] + px * scale, tip[1] + py * scale) for px, py in pts_local]
    if spec["shadow"]:
        shadow = [(x + s * 0.012, y + s * 0.012) for x, y in pts]
        d.polygon(shadow, fill=(0, 0, 0, 60))
    d.polygon(pts, fill=WHITE)
    if spec["outline"]:
        # Thin accent outline so the white cursor stays crisp on light ripples.
        d.line(pts + [pts[0]], fill=(*BLUE_DARK, 255), width=round(s * spec["outline"]), joint="curve")

    tile.alpha_composite(layer)
    return tile


def _tier_for(n: int) -> str:
    """Choose the artwork detail level appropriate for an ``n`` px icon."""
    if n <= 20:
        return "small"
    if n <= 32:
        return "mid"
    return "full"


def _render_at(n: int, variant: str = "ripple") -> Image.Image:
    """Render the mark natively at ``n`` px via a per-size supersampling pass.

    Rendering each size from ``n * SUPERSAMPLE`` keeps strokes crisp; a single
    big master downsampled 32x to 16px would smear the thin rings instead.
    """
    return build_master(variant, size=n * SUPERSAMPLE, tier=_tier_for(n)).resize((n, n), Image.LANCZOS)


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)

    png_path = out_dir / "app_icon.png"
    build_master("ripple", size=MASTER, tier="full").resize((256, 256), Image.LANCZOS).save(png_path)

    # Render distinct artwork per size and embed each as its own frame. The
    # frames must be passed via append_images; with only `sizes=`, Pillow would
    # resize the single base image for every size and discard the per-size work.
    frames = [_render_at(n) for n in ICO_SIZES]
    ico_path = out_dir / "app_icon.ico"
    frames[0].save(
        ico_path,
        format="ICO",
        sizes=[(n, n) for n in ICO_SIZES],
        append_images=frames[1:],
    )

    print(f"wrote {png_path}")
    print(f"wrote {ico_path}")


if __name__ == "__main__":
    main()
