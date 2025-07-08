from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class PageSpeedAnalysis(Base):
    __tablename__ = "pagespeed_analyses"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    strategy = Column(String, nullable=False)  # 'mobile' eller 'desktop'
    performance_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    audits = relationship("PageSpeedAudit", back_populates="analysis", cascade="all, delete-orphan")

class PageSpeedAudit(Base):
    __tablename__ = "pagespeed_audits"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("pagespeed_analyses.id"), nullable=False)

    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    display_value = Column(String, nullable=True)
    audit_score = Column(Float, nullable=True)


    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation til PageSpeedAnalysis
    analysis = relationship("PageSpeedAnalysis", back_populates="audits")