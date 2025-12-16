import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useLoader, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

function EarringMesh({ heightMapUrl, diameter, height, reliefDepth }) {
    const meshRef = useRef();

    // Load the heightmap texture
    const texture = useLoader(THREE.TextureLoader, heightMapUrl);

    // Geometry parameters
    const radius = diameter / 2;
    const segments = 256; // Higher for better displacement detail

    // Material with displacement
    const material = useMemo(() => {
        return new THREE.MeshStandardMaterial({
            color: '#f0e6d2', // Base color (beige-ish)
            displacementMap: texture,
            displacementScale: reliefDepth,
            displacementBias: -reliefDepth, // Push down? Or up. displacement moves vertices along normal.
            // We want the base to be thick, and pattern on top.
            // Actually standard displacement moves along normal.
            // If we use a cylinder, the top face normal is (0,1,0) (if Y up) or (0,0,1) (if Z up).
            // Let's assume Z up for printing intuition, but Three.js is Y up.
            roughness: 0.4,
            metalness: 0.1,
        });
    }, [texture, reliefDepth]);

    // We need a custom geometry or just a plane/cylinder top?
    // A simple cylinder with displacement on the top cap is tricky because standard cylinder UVs might not map the cap perfectly to the image for displacement.
    // Better approach for preview: Just a Plane geometry (Circle) that is displaced, sitting on top of a cylinder.

    return (
        <group rotation={[-Math.PI / 2, 0, 0]}> {/* Rotate to lie flat on grid if needed */}
            {/* 1. Base Cylinder (The solid part) */}
            <mesh position={[0, 0, (height - reliefDepth) / -2]}>
                <cylinderGeometry args={[radius, radius, height - reliefDepth, 64]} />
                <meshStandardMaterial color="#333" /> {/* Dark grey base for contrast? Or make it dual color sim. */}
            </mesh>

            {/* 2. Relief Top (Displaced Plane) */}
            {/* Position it at the top of the base cylinder. Top of cylinder is at y = (h-r)/2 */}
            {/* Actually simply: Base is from 0 down to -(H - R). Relief is from 0 up to R. */}
            {/* Let's try to match the visuals. */}
            <mesh position={[0, (height - reliefDepth) / 2 + 0.01, 0]} rotation={[0, 0, 0]}>
                {/* CircleGeometry: radius, segments */}
                {/* We need high segment count for displacement. */}
                <circleGeometry args={[radius, segments]} />
                {/* We need to rotate the texture? Circle UVs start from center. Heightmap is square. */}
                {/* Usually CircleGeometry UVs map (0.5, 0.5) to center. */}
                {/* Heightmap is a square image. We need the circle to cut out the center circle of the image. */}
                <meshStandardMaterial
                    map={texture} // Show the color?
                    displacementMap={texture}
                    displacementScale={reliefDepth}
                    color="#4ade80" // Green for the pattern
                    roughness={0.4}
                />
            </mesh>
        </group>
    );
}

// Improved implementation using a Plane for better UV mapping stability for displacement
function Earringsim({ heightMapUrl, diameter, height, reliefDepth }) {
    const texture = useLoader(THREE.TextureLoader, heightMapUrl);

    // Plane size should match diameter
    // We use a plane with alphaTest or mask? Or just let the corners be flat?
    // The heightmap has 0 outside the circle.

    // Create a material that uses the heightmap for alpha/transparency too if we want a perfect circle cut?
    // Or just rely on the base cylinder being the main shape.

    return (
        <group>
            {/* Base Disc */}
            <mesh position={[0, -(height - reliefDepth) / 2, 0]} receiveShadow castShadow>
                <cylinderGeometry args={[diameter / 2, diameter / 2, height - reliefDepth, 64]} />
                <meshStandardMaterial color="#e2e8f0" />
            </mesh>

            {/* Relief Layer - Using a highly subdivided plane mapped to the texture */}
            <mesh position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow castShadow>
                <planeGeometry args={[diameter, diameter, 512, 512]} />
                {/* We want the parts with 0 height to be transparent? Or same color as base? */}
                {/* If we want dual color simulation: Base is one color. Relief is another. */}
                {/* We can use offset in displacement. 0 is base level. */}
                <meshStandardMaterial
                    color="#0d9488" // Teal color for relief
                    displacementMap={texture}
                    displacementScale={reliefDepth}
                    alphaMap={texture} // Optional: hide zero height areas?
                    // alphaTest={0.01}
                    transparent={true}
                    roughness={0.6}
                />
            </mesh>
        </group>
    )
}

export default function Viewer({ heightMapUrl, params }) {
    if (!heightMapUrl) return (
        <div className="w-full h-full flex items-center justify-center text-slate-500">
            Generating Preview...
        </div>
    );

    return (
        <div className="w-full h-full bg-slate-950 relative">
            <Canvas shadows camera={{ position: [0, 20, 20], fov: 45 }}>
                <fog attach="fog" args={['#020617', 10, 50]} />
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 10, 5]} intensity={1.5} castShadow />
                <spotLight position={[-10, 10, -5]} intensity={1} />

                <Suspense fallback={null}>
                    <Earringsim
                        heightMapUrl={heightMapUrl}
                        diameter={params.diameter}
                        height={params.height}
                        reliefDepth={params.relief_depth}
                    />
                    <Environment preset="city" />
                    <ContactShadows position={[0, -2, 0]} opacity={0.5} scale={40} blur={2} far={4.5} />
                </Suspense>

                <OrbitControls minPolarAngle={0} maxPolarAngle={Math.PI / 2} />
            </Canvas>
            <div className="absolute bottom-4 right-4 text-xs text-slate-500">
                LMB to Rotate • RMB to Pan • Scroll to Zoom
            </div>
        </div>
    );
}
