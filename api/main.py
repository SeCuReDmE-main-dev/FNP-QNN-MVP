"""
FNP-QNN Real API Server
Connects PhiTroN OS to actual quantum neural processing
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import subprocess
import os
import sys

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.phi_framework import PhiFramework
import numpy as np

app = FastAPI(title="FNP-QNN API", description="Real quantum neural network API")

# CORS for PhiTroN OS connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global phi framework instance
phi_engine = PhiFramework()

@app.get("/")
async def root():
    return {"message": "FNP-QNN API Active", "phi": phi_engine.phi}

@app.post("/execute-command")
async def execute_command(command_data: dict):
    """Execute real terminal commands"""
    command = command_data.get("command", "")
    
    if not command:
        raise HTTPException(status_code=400, detail="No command provided")
    
    try:
        # Special FNP-QNN commands
        if command.startswith("phi-"):
            return await handle_phi_command(command)
        elif command.startswith("quantum-"):
            return await handle_quantum_command(command)
        elif command.startswith("neural-"):
            return await handle_neural_command(command)
        
        # Real system commands (safe list)
        safe_commands = ["ls", "pwd", "whoami", "date", "echo", "ps", "node -v", "python --version"]
        
        if any(command.startswith(safe) for safe in safe_commands):
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            return {
                "success": True,
                "output": result.stdout if result.stdout else result.stderr,
                "type": "system"
            }
        else:
            return {
                "success": False,
                "error": f"Command '{command}' not allowed",
                "type": "error"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "type": "error"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": "error"
        }

async def handle_phi_command(command: str):
    """Handle φ-framework commands"""
    try:
        if command == "phi-status":
            particles = phi_engine.generate_quantum_particles(100)
            return {
                "success": True,
                "output": f"φ-Framework Status:\nGolden Ratio: {phi_engine.phi}\nQuantum Particles: {len(particles)} generated\nResonance: {phi_engine.phi * 40:.2f} Hz",
                "type": "phi-system",
                "data": {"phi": phi_engine.phi, "particles": len(particles)}
            }
        
        elif command == "phi-calc":
            # Real calculation
            c3_result = phi_engine.calculate_c3_formula(2.5, 1.2, 0.8, 1.5)
            return {
                "success": True,
                "output": f"C³ Formula Result: {c3_result:.6f}\nφ = {phi_engine.phi}\nQuantum Field Strength: {c3_result * phi_engine.phi:.6f}",
                "type": "phi-system",
                "data": {"c3": c3_result, "phi": phi_engine.phi}
            }
        
        elif command == "phi-map":
            # Real brain mapping
            hippocampus = phi_engine.map_brain_region("hippocampus", (20, 15, 10))
            return {
                "success": True,
                "output": f"Brain Region Mapped:\nHippocampus: {hippocampus.shape}\nComplex quantum field generated\nMean field strength: {np.mean(np.abs(hippocampus)):.6f}",
                "type": "phi-system",
                "data": {"region": "hippocampus", "shape": hippocampus.shape}
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown phi command: {command}",
                "type": "error"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Phi command error: {str(e)}",
            "type": "error"
        }

async def handle_quantum_command(command: str):
    """Handle quantum processing commands"""
    try:
        if command == "quantum-test":
            particles = phi_engine.generate_quantum_particles(50)
            coherence = np.mean([abs(p.amplitude) for p in particles])
            
            return {
                "success": True,
                "output": f"Quantum Test Results:\nParticles: {len(particles)}\nCoherence: {coherence:.4f}\nEntanglement: Active\nPhase Correlation: {np.mean([p.phase for p in particles]):.4f}",
                "type": "quantum-system",
                "data": {"particles": len(particles), "coherence": coherence}
            }
        
        elif command == "quantum-state":
            # Generate actual quantum state
            state = phi_engine.quantum_states[0] if phi_engine.quantum_states else None
            if not state:
                particles = phi_engine.generate_quantum_particles(1)
                state = particles[0]
            
            return {
                "success": True,
                "output": f"Quantum State:\n|ψ⟩ = {state.amplitude}\nPhase: {state.phase:.4f}\nFrequency: {state.frequency:.4f} Hz\nResonance: {state.quantum_resonance:.4f}",
                "type": "quantum-system",
                "data": {"amplitude": str(state.amplitude), "phase": state.phase}
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown quantum command: {command}",
                "type": "error"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Quantum command error: {str(e)}",
            "type": "error"
        }

async def handle_neural_command(command: str):
    """Handle neural network commands"""
    try:
        if command == "neural-map":
            # Real neural mapping
            regions = ["hippocampus", "frontal_cortex", "cerebellum"]
            mapped_regions = {}
            
            for region in regions:
                mapping = phi_engine.map_brain_region(region, (10, 10, 8))
                mapped_regions[region] = {
                    "shape": mapping.shape,
                    "mean_strength": float(np.mean(np.abs(mapping)))
                }
            
            output = "Neural Mapping Complete:\n"
            for region, data in mapped_regions.items():
                output += f"{region}: {data['shape']}, strength: {data['mean_strength']:.4f}\n"
            
            return {
                "success": True,
                "output": output,
                "type": "neural-system",
                "data": mapped_regions
            }
        
        elif command == "neural-cure":
            # Generate real cure algorithm
            deficit_pos = (10, 8, 5)  # Example coordinates
            cure_algo = phi_engine.generate_cure_algorithm(deficit_pos, "test_deficit")
            
            return {
                "success": True,
                "output": f"Cure Algorithm Generated:\nFrequency: {cure_algo['therapeutic_frequency']:.2f} Hz\nRecovery Time: {cure_algo['estimated_recovery_time']:.1f}\nPlasticity Factor: {cure_algo['neural_plasticity_factor']:.4f}",
                "type": "neural-system",
                "data": cure_algo
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown neural command: {command}",
                "type": "error"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Neural command error: {str(e)}",
            "type": "error"
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time communication with PhiTroN OS"""
    await websocket.accept()
    
    try:
        while True:
            # Receive command from PhiTroN OS
            data = await websocket.receive_text()
            command_data = json.loads(data)
            
            # Process command
            result = await execute_command(command_data)
            
            # Send response back
            await websocket.send_text(json.dumps(result))
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "phi_framework": "operational",
        "golden_ratio": phi_engine.phi,
        "quantum_particles": len(phi_engine.quantum_states)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)