import React, { useRef, useMemo, Suspense, useState, useEffect } from 'react';
import { Canvas, useLoader, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera, ContactShadows, useGLTF } from '@react-three/drei';
import * as THREE from 'three';

// Real 3D mesh loader - shows actual vector geometry with sharp edges!
function RealEarringMesh({ modelUrl }) {
    const { scene } = useGLTF(modelUrl);

    // Clone the scene to avoid mutations
    const clonedScene = useMemo(() => {
        const clone = scene.clone();

        // Apply materials to different parts for dual-color preview
        clone.traverse((child) => {
            if (child.isMesh) {
                // Base_Scheibe = base color (beige/cream)
                // Muster_Relief = pattern color (teal/green)
                if (child.name.includes('Base')) {
                    child.material = new THREE.MeshStandardMaterial({
                        color: '#e2e8f0', // Light gray/beige for base
                        roughness: 0.4,
                        metalness: 0.1,
                    });
                } else if (child.name.includes('Muster')) {
                    child.material = new THREE.MeshStandardMaterial({
                        color: '#0d9488', // Teal for relief pattern
                        roughness: 0.5,
                        metalness: 0.1,
                    });
                }
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });

        return clone;
    }, [scene]);

    return <primitive object={clonedScene} />;
}

export default function Viewer({ heightMapUrl, params }) {
    const [modelUrl, setModelUrl] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch the actual 3D model (GLB format)
        const fetchModel = async () => {
            setLoading(true);
            try {
                const url = `/api/preview3d?seed=${params.seed}&diameter=${params.diameter}&height=${params.height}&relief_depth=${params.relief_depth}&t=${Date.now()}`;
                const res = await fetch(url);
                const blob = await res.blob();
                const objectUrl = URL.createObjectURL(blob);
                setModelUrl(objectUrl);
            } catch (error) {
                console.error("Failed to load 3D model", error);
            } finally {
                setLoading(false);
            }
        };

        fetchModel();

        // Cleanup
        return () => {
            if (modelUrl) URL.revokeObjectURL(modelUrl);
        };
    }, [params.seed, params.diameter, params.height, params.relief_depth]);

    if (loading || !modelUrl) {
        return (
            <div className="w-full h-full flex items-center justify-center text-slate-500">
                Generating 3D Preview...
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-slate-950 relative">
            <Canvas shadows camera={{ position: [15, 15, 15], fov: 50 }}>
                <fog attach="fog" args={['#020617', 10, 60]} />
                <ambientLight intensity={0.7} />
                <directionalLight position={[10, 15, 10]} intensity={1.8} castShadow />
                <directionalLight position={[-5, 10, -5]} intensity={0.6} />
                <spotLight position={[0, 20, 0]} intensity={0.5} />

                <Suspense fallback={null}>
                    <RealEarringMesh modelUrl={modelUrl} />
                    <Environment preset="city" />
                    <ContactShadows position={[0, -2, 0]} opacity={0.5} scale={40} blur={2} far={4.5} />
                </Suspense>

                <OrbitControls
                    enableDamping
                    dampingFactor={0.05}
                    minDistance={5}
                    maxDistance={50}
                />
            </Canvas>
            <div className="absolute bottom-4 right-4 text-xs text-slate-500 bg-slate-900/50 px-2 py-1 rounded">
                Real Vector Geometry • LMB Rotate • RMB Pan • Scroll Zoom
            </div>
        </div>
    );
}
