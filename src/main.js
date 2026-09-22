import "./style.css";
import { loadPyodide } from "pyodide";
import { PLAYER_1, PLAYER_2, SYSTEM } from "@rcade/plugin-input-classic";
import { PLAYER_1 as SPINNER_PLAYER_1, PLAYER_2 as SPINNER_PLAYER_2 } from "@rcade/plugin-input-spinners";
import gameCode from "./game.py?raw";
import wheels from "virtual:pyodide-wheels";

function setupKeyboardFallback() {
    const bindings = {
        KeyW: [PLAYER_1.DPAD, "up"],
        KeyS: [PLAYER_1.DPAD, "down"],
        KeyA: [PLAYER_1.DPAD, "left"],
        KeyD: [PLAYER_1.DPAD, "right"],
        KeyF: [PLAYER_1, "A"],
        KeyG: [PLAYER_1, "B"],
        KeyI: [PLAYER_2.DPAD, "up"],
        KeyK: [PLAYER_2.DPAD, "down"],
        KeyJ: [PLAYER_2.DPAD, "left"],
        KeyL: [PLAYER_2.DPAD, "right"],
        Semicolon: [PLAYER_2, "A"],
        Quote: [PLAYER_2, "B"],
        Digit1: [SYSTEM, "ONE_PLAYER"],
        Digit2: [SYSTEM, "TWO_PLAYER"],
    };

    const setInput = (event, pressed) => {
        const binding = bindings[event.code];
        if (!binding) {
            return;
        }

        event.preventDefault();
        binding[0][binding[1]] = pressed;
    };

    window.addEventListener("keydown", (event) => setInput(event, true));
    window.addEventListener("keyup", (event) => setInput(event, false));
}

async function main() {
    setupKeyboardFallback();

    const pyodide = await loadPyodide({
        indexURL: "/assets",
    });

    // Set up SDL2 canvas for pygame rendering
    const canvas = document.getElementById("canvas");
    pyodide.canvas.setCanvas2D(canvas);

    // Load micropip for installing local wheels
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");

    // Install all wheels from local assets
    for (const wheel of wheels) {
        await micropip.install(`/assets/${wheel}`);
    }

    // Create input bridge - called from Python
    const getInput = () => ({
        p1: {
            up: PLAYER_1.DPAD.up,
            down: PLAYER_1.DPAD.down,
            left: PLAYER_1.DPAD.left,
            right: PLAYER_1.DPAD.right,
            a: PLAYER_1.A,
            b: PLAYER_1.B,
            spinner: SPINNER_PLAYER_1.SPINNER.consume_step_delta(),
        },
        p2: {
            up: PLAYER_2.DPAD.up,
            down: PLAYER_2.DPAD.down,
            left: PLAYER_2.DPAD.left,
            right: PLAYER_2.DPAD.right,
            a: PLAYER_2.A,
            b: PLAYER_2.B,
            spinner: SPINNER_PLAYER_2.SPINNER.consume_step_delta(),
        },
        system: {
            start_1p: SYSTEM.ONE_PLAYER,
            start_2p: SYSTEM.TWO_PLAYER,
        },
    });

    pyodide.globals.set("_get_input", getInput);

    // Run the game
    await pyodide.runPythonAsync(gameCode);
}

main();
