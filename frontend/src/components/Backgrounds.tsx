

export function GridPattern() {
    return (
        <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.03]"
            style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
        </div>
    );
}

export function MeshGradient() {
    return (
        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-blue-400/20 blur-[100px] pointer-events-none z-0 mix-blend-multiply animate-pulse" style={{ animationDuration: '10s' }} />
    );
}
