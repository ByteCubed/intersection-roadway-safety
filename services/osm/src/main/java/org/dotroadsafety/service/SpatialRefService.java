package org.dotroadsafety.service;

import org.dotroadsafety.model.Spatial_ref_sys;
import org.dotroadsafety.repository.Spatial_ref_sysRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class SpatialRefService {

    @Autowired
    Spatial_ref_sysRepository spatialRefRepository;

    public Spatial_ref_sys findSpatialRefById(Long osmId) {
        Optional<Spatial_ref_sys> spatialRefs = spatialRefRepository.findById(osmId);
        return spatialRefs.get();
    }

    public Iterable<Spatial_ref_sys> findSpatialRefsByName(String spatialRefName) {
        return spatialRefRepository.findSpatialRefsByName(spatialRefName);
    }

    public Iterable<Spatial_ref_sys> findSpatialRefsLikeName(String spatialRefName) {
        return spatialRefRepository.findSpatialRefsLikeName(spatialRefName);
    }

    public Iterable<Spatial_ref_sys> findAllSpatialRefsWithPaging(int pageSize) {
        return spatialRefRepository.findAll(Pageable.ofSize(pageSize));
    }

    public Iterable<Spatial_ref_sys> findAllSpatialRefsByPageAndSize(int pageNumber, int pageSize) {
        return spatialRefRepository.findAll(PageRequest.of(pageNumber, pageSize));
    }

    public Iterable<Spatial_ref_sys> findAllSpatialRefs() {
        return spatialRefRepository.findAll();
    }

}
