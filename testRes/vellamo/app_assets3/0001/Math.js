var Vector3D = function ( x, y, z ) {
    this.initialize(
        x || 0,
        y || 0,
        z || 0
    );
};

Vector3D.prototype = {
    x: null,    y: null,    z: null,
    sx: null,   sy: null,   sz: null,
	userData: null,
    dx: null,   dy: null,   dz: null,
    tx: null,   ty: null,   tz: null,
	oll: null,
	initialize: function(x, y, z){
        var m = this;   m.x = x;    m.y = y;    m.z = z;
	},
	copy: function(v){
        var m = this;   m.x = v.x;  m.y = v.y;  m.z = v.z;
	},
	sub: function(v){
        var m = this;   m.x -= v.x; m.y -= v.y; m.z -= v.z;
	},
    cross: function(v){
        var m = this;   m.tx = m.x; m.ty = m.y; m.tz = m.z;
        m.x = m.ty * v.z - m.tz * v.y;
        m.y = m.tz * v.x - m.tx * v.z;
        m.z = m.tx * v.y - m.ty * v.x;
	},
	multiply: function(s){
        var m = this;   m.x *= s;   m.y *= s;   m.z *= s;
	},
	length: function(){
        var m = this;
        return Math.sqrt(m.x * m.x + m.y * m.y + m.z * m.z);
	},
	normalize: function(){
        var m = this;
        if (m.length() > 0)
            m.ool = 1.0 / m.length();
		else
            m.ool = 0;
        m.x *= m.ool;   m.y *= m.ool;   m.z *= m.ool;
		return this;
	},
	dot: function(v){
        var m = this;
        return m.x * v.x + m.y * v.y + m.z * v.z;
	},
	clone: function(){
        var m = this;
        return new Vector3D(m.x, m.y, m.z);
	},
}

var Matrix3D = function() {
    this.initialize();
};

Matrix3D.prototype = {
    n11: null,  n12: null,  n13: null,  n14: null,
    n21: null,  n22: null,  n23: null,  n24: null,
    n31: null,  n32: null,  n33: null,  n34: null,
    x: new Vector3D(0,0,0),
    y: new Vector3D(0,0,0),
    z: new Vector3D(0,0,0),
    initialize: function(){
        var m = this;
        m.n11 = 1;  m.n12 = 0;  m.n13 = 0;  m.n14 = 0;
        m.n21 = 0;  m.n22 = 1;  m.n23 = 0;  m.n24 = 0;
        m.n31 = 0;  m.n32 = 0;  m.n33 = 1;  m.n34 = 0;
        m.x = new Vector3D(0,0,0);
        m.y = new Vector3D(0,0,0);
        m.z = new Vector3D(0,0,0);
    },
    lookAt: function(eye, center, up){
        var m = this;
        m.z.copy(center);   m.z.sub(eye);   m.z.normalize();
        m.x.copy(m.z);      m.x.cross(up);  m.x.normalize();
        m.y.copy(m.x);      m.y.cross(m.z); m.y.normalize();
        m.n11 = m.x.x;      m.n12 = m.x.y;  m.n13 = m.x.z;  m.n14 = -m.x.dot(eye);
        m.n21 = m.y.x;      m.n22 = m.y.y;  m.n23 = m.y.z;  m.n24 = -m.y.dot(eye);
        m.n31 = m.z.x;      m.n32 = m.z.y;  m.n33 = m.z.z;  m.n34 = -m.z.dot(eye);
    },
    transform: function(v){
        var m = this;
        var vx = v.x, vy = v.y, vz = v.z;
        v.x = m.n11 * vx + m.n12 * vy + m.n13 * vz + m.n14;
        v.y = m.n21 * vx + m.n22 * vy + m.n23 * vz + m.n24;
        v.z = m.n31 * vx + m.n32 * vy + m.n33 * vz + m.n34;
    },
}
