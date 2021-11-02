package org.dotroadsafety.service;

import org.dotroadsafety.model.Crashes;
import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.repository.CrashesRepository;
import org.dotroadsafety.repository.Planet_osm_roadsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class CrashesService {

    @Autowired
    CrashesRepository crashesRepository;

    public Crashes findCrashById(Long uid) {
        Optional<Crashes> crashes = crashesRepository.findById(uid);
        return crashes.get();
    }

    public Iterable<Crashes> findCrashesByAddress(String address) {
        return crashesRepository.findAllCrashesByAddress(address);
    }

    public Iterable<Crashes> findAllCrashesWithPaging(int pageSize) {
        return crashesRepository.findAll(Pageable.ofSize(pageSize));
    }

    public Iterable<Crashes> findAllCrashesByPageAndSize(int pageNumber, int pageSize) {
        return crashesRepository.findAll(PageRequest.of(pageNumber, pageSize));
    }

    public Iterable<Crashes> findAllCrashes() {
        return crashesRepository.findAll();
    }

    public Iterable<Crashes> findCrashesByCrimeId(String crimeId) {
        return crashesRepository.findByCrimeID(crimeId);
    }
}
